
const $ = (id) => document.getElementById(id);

let currentIndex = 0;
let totalQuestions = 16;
let score = 0;
let currentQuestion = null;
let selectedAnswer = null;
let answered = false;
let gameOver = false;
let usedLifelines = new Set();

async function postJSON(url, data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            result.error || `Request failed (${response.status}).`
        );
    }

    return result;
}

function showMessage(message, type = "info") {
    const feedback = $("feedback");

    if (feedback) {
        feedback.textContent = message;
        feedback.className = `feedback ${type}`;
        feedback.hidden = false;
    } else {
        alert(message);
    }
}

function clearMessage() {
    const feedback = $("feedback");

    if (feedback) {
        feedback.textContent = "";
        feedback.hidden = true;
    }
}

function setText(id, value) {
    const element = $(id);
    if (element) element.textContent = value ?? "";
}

function formatRupees(amount) {
    return "₹" + Number(amount || 0).toLocaleString("en-IN");
}

function syncLifelines(used) {
    if (!Array.isArray(used)) return;

    usedLifelines = new Set(used);

    const buttons = {
        fifty_fifty: "fiftyFiftyBtn",
        audience_poll: "audiencePollBtn",
        phone_friend: "phoneFriendBtn"
    };

    for (const [name, id] of Object.entries(buttons)) {
        const button = $(id);

        if (button) {
            button.disabled =
                usedLifelines.has(name) || gameOver || answered;
            button.classList.toggle(
                "lifeline-used",
                usedLifelines.has(name)
            );
        }
    }
}

function updateProgress(data) {
    currentIndex = data.index ?? currentIndex;
    totalQuestions = data.total ?? totalQuestions;
    score = data.score ?? score;

    setText(
        "questionCounter",
        `Question ${currentIndex + 1} of ${totalQuestions}`
    );
    setText("score", `Score: ${score}`);
    setText("currentPrize", `Current prize: ${formatRupees(data.prize)}`);
    setText("winnings", `Secured winnings: ${formatRupees(data.winnings)}`);

    const progress = $("progressBar");

    if (progress) {
        progress.style.width =
            `${((currentIndex + 1) / totalQuestions) * 100}%`;
    }

    syncLifelines(data.used_lifelines);
}

function hideLifelineResults() {
    const pollSection = $("audiencePollResults");
    const friendSection = $("phoneFriendResults");

    if (pollSection) pollSection.hidden = true;
    if (friendSection) friendSection.hidden = true;

    const pollBars = $("audiencePollBars");
    if (pollBars) pollBars.replaceChildren();

    setText("friendAnswer", "");
    setText("friendConfidence", "");
    setText("friendReason", "");
}

async function loadQuestion() {
    if (gameOver) return;

    answered = false;
    selectedAnswer = null;
    currentQuestion = null;

    clearMessage();
    hideLifelineResults();

    const optionsContainer = $("options");

    if (optionsContainer) {
        optionsContainer.replaceChildren();
    }

    setText("questionText", "Loading question...");

    const submitButton = $("submitAnswerBtn");
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.remove("ready-to-submit");
    }

    const nextButton = $("nextQuestionBtn");
    if (nextButton) nextButton.hidden = true;

    try {
        const data = await postJSON("/get-question", {});

        if (!data.question || !Array.isArray(data.options)) {
            throw new Error("The server did not return a valid question.");
        }

        currentQuestion = data;
        updateProgress(data);
        setText("questionText", data.question);

        if (optionsContainer) {
            data.options.forEach((option, index) => {
                const button = document.createElement("button");

                button.type = "button";
                button.className = "option-btn";
                button.setAttribute("aria-pressed", "false");
                button.textContent =
                    `${String.fromCharCode(65 + index)}. ${option}`;

                button.addEventListener("click", () => {
                    selectOption(option, button);
                });

                optionsContainer.appendChild(button);
            });
        }

        const quizScreen = $("quizScreen");
        if (quizScreen) quizScreen.hidden = false;

        const resultScreen = $("resultScreen");
        if (resultScreen) resultScreen.hidden = true;

        syncLifelines(data.used_lifelines);

        if (submitButton) submitButton.disabled = true;

    } catch (error) {
        setText("questionText", "Question could not be loaded.");

        showMessage(
            `${error.message} Please return to the subjects page and start a new quiz.`,
            "error"
        );
    }
}

function selectOption(option, button) {
    if (answered || gameOver || button.disabled) return;

    selectedAnswer = option;

    document.querySelectorAll(".option-btn").forEach((item) => {
        item.classList.remove("selected");
        item.setAttribute("aria-pressed", "false");
    });

    button.classList.add("selected");
    button.setAttribute("aria-pressed", "true");

    const submitButton = $("submitAnswerBtn");

    if (submitButton) {
        submitButton.disabled = false;
        submitButton.classList.add("ready-to-submit");
    }
}

async function submitAnswer() {
    if (answered || gameOver) return;

    if (selectedAnswer === null) {
        showMessage("Please select an answer first.", "error");
        return;
    }

    const submitButton = $("submitAnswerBtn");

    if (submitButton) submitButton.disabled = true;

    try {
        const data = await postJSON("/check-answer", {
            index: currentIndex,
            answer: selectedAnswer
        });

        answered = true;
        score = data.score ?? score;

        setText("score", `Score: ${score}`);

        document.querySelectorAll(".option-btn").forEach((button) => {
            const option = button.textContent.replace(/^[A-D]\.\s*/, "");

            button.disabled = true;

            if (option === data.correct_answer) {
                button.classList.add("correct");
            } else if (option === selectedAnswer && !data.correct) {
                button.classList.add("incorrect");
            }
        });

        showMessage(
            `${data.correct ? "Correct!" : "Incorrect."} ${data.explanation || ""}`,
            data.correct ? "success" : "error"
        );

        setText("winnings", `Winnings: ${formatRupees(data.winnings)}`);

        if (data.game_over) {
            showResults(data.message, data.winnings, data.score);
            return;
        }

        const nextButton = $("nextQuestionBtn");
        if (nextButton) nextButton.hidden = false;

        syncLifelines(Array.from(usedLifelines));

    } catch (error) {
        showMessage(error.message, "error");

        if (submitButton) submitButton.disabled = false;
    }
}

function showResults(message, winnings, finalScore) {
    gameOver = true;

    const quizScreen = $("quizScreen");
    if (quizScreen) quizScreen.hidden = true;

    const resultScreen = $("resultScreen");
    if (resultScreen) resultScreen.hidden = false;

    setText("resultMessage", message || "Game over!");
    setText("finalScore", `${finalScore ?? score} / ${totalQuestions}`);
    setText("finalWinnings", `Virtual winnings: ${formatRupees(winnings)}`);

    syncLifelines(Array.from(usedLifelines));
}

async function nextQuestion() {
    if (!answered || gameOver) return;
    await loadQuestion();
}

function renderAudiencePoll(poll) {
    const section = $("audiencePollResults");
    const container = $("audiencePollBars");

    if (!section || !container) return;

    container.replaceChildren();

    for (const [option, rawPercentage] of Object.entries(poll || {})) {
        const parsed = Number(rawPercentage);
        const percentage = Number.isFinite(parsed)
            ? Math.min(100, Math.max(0, parsed))
            : 0;

        const row = document.createElement("div");
        row.className = "poll-row";

        const label = document.createElement("span");
        label.className = "poll-label";
        label.textContent = option;

        const track = document.createElement("div");
        track.className = "poll-bar-background";

        const bar = document.createElement("div");
        bar.className = "poll-bar";
        bar.style.width = `${percentage}%`;
        bar.setAttribute("role", "progressbar");
        bar.setAttribute("aria-valuemin", "0");
        bar.setAttribute("aria-valuemax", "100");
        bar.setAttribute("aria-valuenow", String(percentage));
        bar.setAttribute("aria-label", `${option}: ${percentage}%`);

        track.appendChild(bar);

        const value = document.createElement("span");
        value.className = "poll-percentage";
        value.textContent = `${percentage}%`;

        row.append(label, track, value);
        container.appendChild(row);
    }

    section.hidden = false;
}

function renderPhoneFriend(data) {
    const section = $("phoneFriendResults");

    if (!section) return;

    setText("friendAnswer", `Your friend's suggestion: ${data.answer}`);

    const confidence = Number(data.confidence_percentage);
    const safeConfidence = Number.isFinite(confidence)
        ? Math.min(100, Math.max(0, confidence))
        : 0;

    const confidenceText = $("friendConfidence");

    if (confidenceText) {
        confidenceText.replaceChildren();

        const label = document.createElement("span");
        label.className = "friend-confidence-label";
        label.textContent = `Confidence: ${safeConfidence}%`;

        const track = document.createElement("div");
        track.className = "friend-confidence-track";

        const fill = document.createElement("div");
        fill.className = "friend-confidence-fill";
        fill.style.width = `${safeConfidence}%`;
        fill.setAttribute("role", "progressbar");
        fill.setAttribute("aria-valuemin", "0");
        fill.setAttribute("aria-valuemax", "100");
        fill.setAttribute("aria-valuenow", String(safeConfidence));
        fill.setAttribute(
            "aria-label",
            `Friend confidence: ${safeConfidence}%`
        );

        track.appendChild(fill);
        confidenceText.append(label, track);
    }

    setText("friendReason", data.reason || "Your friend has no extra explanation.");

    section.hidden = false;
}

async function useLifeline(name, endpoint) {
    if (gameOver || answered || !currentQuestion) return;

    if (usedLifelines.has(name)) {
        showMessage("You have already used this lifeline.", "error");
        return;
    }

    const buttonIds = {
        fifty_fifty: "fiftyFiftyBtn",
        audience_poll: "audiencePollBtn",
        phone_friend: "phoneFriendBtn"
    };

    const lifelineButton = $(buttonIds[name]);

    if (lifelineButton) lifelineButton.disabled = true;

    try {
        const data = await postJSON(endpoint, { index: currentIndex });

        syncLifelines(data.used_lifelines);

        if (name === "fifty_fifty") {
            const remaining = new Set(data.options);

            document.querySelectorAll(".option-btn").forEach((button) => {
                const option = button.textContent.replace(/^[A-D]\.\s*/, "");

                if (!remaining.has(option)) {
                    button.disabled = true;
                    button.classList.add("eliminated");
                    button.classList.remove("selected");
                    button.setAttribute("aria-pressed", "false");

                    if (selectedAnswer === option) {
                        selectedAnswer = null;
                    }
                }
            });

            const submitButton = $("submitAnswerBtn");

            if (selectedAnswer === null && submitButton) {
                submitButton.disabled = true;
                submitButton.classList.remove("ready-to-submit");
            }

            showMessage(
                "50:50 used. Two incorrect options have been eliminated."
            );

        } else if (name === "audience_poll") {
            renderAudiencePoll(data.poll);

            showMessage("Simulated Audience Poll: results are ready.");

        } else if (name === "phone_friend") {
            renderPhoneFriend(data);

            showMessage("Your friend has shared their suggestion.");
        }

    } catch (error) {
        showMessage(error.message, "error");

        if (lifelineButton) {
            lifelineButton.disabled =
                usedLifelines.has(name) || answered || gameOver;
        }
    }
}

async function quitGame() {
    if (gameOver) return;

    if (!confirm("Are you sure you want to quit this game?")) return;

    try {
        const data = await postJSON("/quit-game", {});
        showResults(data.message, data.winnings, data.score);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function goHome() {
    window.location.href = "/";
}

document.addEventListener("DOMContentLoaded", () => {
    if ($("submitAnswerBtn")) {
        $("submitAnswerBtn").addEventListener("click", submitAnswer);
    }

    if ($("nextQuestionBtn")) {
        $("nextQuestionBtn").addEventListener("click", nextQuestion);
    }

    if ($("fiftyFiftyBtn")) {
        $("fiftyFiftyBtn").addEventListener("click", () =>
            useLifeline("fifty_fifty", "/use-fifty-fifty")
        );
    }

    if ($("audiencePollBtn")) {
        $("audiencePollBtn").addEventListener("click", () =>
            useLifeline("audience_poll", "/use-audience-poll")
        );
    }

    if ($("phoneFriendBtn")) {
        $("phoneFriendBtn").addEventListener("click", () =>
            useLifeline("phone_friend", "/use-phone-friend")
        );
    }

    if ($("quitGameBtn")) {
        $("quitGameBtn").addEventListener("click", quitGame);
    }

    if ($("homeButton")) {
        $("homeButton").addEventListener("click", goHome);
    }

    if ($("resultHomeButton")) {
        $("resultHomeButton").addEventListener("click", goHome);
    }

    if ($("playAgainButton")) {
        $("playAgainButton").addEventListener("click", goHome);
    }

    loadQuestion();
});
