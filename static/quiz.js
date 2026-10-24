
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
        throw new Error(result.error || `Request failed (${response.status}).`);
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
            button.disabled = usedLifelines.has(name) || gameOver || answered;
        }
    }
}

function updateProgress(data) {
    currentIndex = data.index ?? currentIndex;
    totalQuestions = data.total ?? totalQuestions;
    score = data.score ?? score;

    setText("questionCounter",
        `Question ${currentIndex + 1} of ${totalQuestions}`);
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

async function loadQuestion() {
    if (gameOver) return;

    answered = false;
    selectedAnswer = null;
    currentQuestion = null;
    clearMessage();

    const optionsContainer = $("options");
    if (optionsContainer) optionsContainer.replaceChildren();

    setText("questionText", "Loading question...");

    const submitButton = $("submitAnswerBtn");
    if (submitButton) submitButton.disabled = true;

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
                button.textContent =
                    `${String.fromCharCode(65 + index)}. ${option}`;

                button.addEventListener("click", () => selectOption(option, button));
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
    if (answered || gameOver) return;

    selectedAnswer = option;

    document.querySelectorAll(".option-btn").forEach((item) => {
        item.classList.remove("selected");
    });

    button.classList.add("selected");

    const submitButton = $("submitAnswerBtn");
    if (submitButton) submitButton.disabled = false;
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

async function useLifeline(name, endpoint) {
    if (gameOver || answered || !currentQuestion) return;

    if (usedLifelines.has(name)) {
        showMessage("You have already used this lifeline.", "error");
        return;
    }

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
                }
            });

            showMessage("50:50 used. Two incorrect options have been eliminated.");
        } else if (name === "audience_poll") {
            const poll = Object.entries(data.poll || {})
                .map(([option, percentage]) => `${option}: ${percentage}%`)
                .join("\n");

            showMessage(`Simulated Audience Poll:\n${poll}`);
        } else if (name === "phone_friend") {
            showMessage(
                `Your friend suggests: ${data.answer}\n` +
                `Confidence: ${data.confidence_percentage}%\n${data.reason}`
            );
        }

    } catch (error) {
        showMessage(error.message, "error");
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
            useLifeline("fifty_fifty", "/use-fifty-fifty"));
    }

    if ($("audiencePollBtn")) {
        $("audiencePollBtn").addEventListener("click", () =>
            useLifeline("audience_poll", "/use-audience-poll"));
    }

    if ($("phoneFriendBtn")) {
        $("phoneFriendBtn").addEventListener("click", () =>
            useLifeline("phone_friend", "/use-phone-friend"));
    }

    if ($("quitGameBtn")) {
        $("quitGameBtn").addEventListener("click", quitGame);
    }

    if ($("homeButton")) $("homeButton").addEventListener("click", goHome);
    if ($("resultHomeButton")) {
        $("resultHomeButton").addEventListener("click", goHome);
    }

    if ($("playAgainButton")) {
        $("playAgainButton").addEventListener("click", goHome);
    }

    loadQuestion();
});
