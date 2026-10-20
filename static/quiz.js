
const subject = window.quizSubject || document.body.dataset.subject || "";

let currentIndex = 0;
let totalQuestions = 16;
let score = 0;
let currentQuestion = null;
let selectedAnswer = null;
let answered = false;
let gameOver = false;
let usedLifelines = new Set();

const $ = (id) => document.getElementById(id);

async function postJSON(url, data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(result.error || "Something went wrong.");
    }

    return result;
}

function showMessage(message, type = "info") {
    const feedback = $("feedback");
    if (!feedback) {
        alert(message);
        return;
    }

    feedback.textContent = message;
    feedback.className = `feedback ${type}`;
    feedback.hidden = false;
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
    if (element) element.textContent = value;
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
        phone_friend: "phoneFriendBtn",
        ask_expert: "askExpertBtn"
    };

    for (const [name, id] of Object.entries(buttons)) {
        const button = $(id);
        if (button) {
            button.disabled = usedLifelines.has(name) || gameOver;
        }
    }
}

function updateProgress(data) {
    currentIndex = data.index ?? currentIndex;
    totalQuestions = data.total ?? totalQuestions;
    score = data.score ?? score;

    setText("questionCounter", `Question ${currentIndex + 1} of ${totalQuestions}`);
    setText("score", score);
    setText("currentPrize", formatRupees(data.prize));
    setText("winnings", formatRupees(data.winnings));

    const progress = $("progressBar");
    if (progress) {
        progress.style.width = `${((currentIndex + 1) / totalQuestions) * 100}%`;
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

    const questionElement = $("questionText");
    if (questionElement) questionElement.textContent = "Loading question...";

    try {
        const data = await postJSON("/get-question", {});
        currentQuestion = data;
        updateProgress(data);

        if (questionElement) questionElement.textContent = data.question;

        if (optionsContainer) {
            data.options.forEach((option, index) => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "option-btn";
                button.textContent = `${String.fromCharCode(65 + index)}. ${option}`;
                button.addEventListener("click", () => selectOption(option, button));
                optionsContainer.appendChild(button);
            });
        }

        const submitButton = $("submitAnswerBtn");
        if (submitButton) submitButton.disabled = false;

        const nextButton = $("nextQuestionBtn");
        if (nextButton) nextButton.hidden = true;

        const resultScreen = $("resultScreen");
        if (resultScreen) resultScreen.hidden = true;

        const quizScreen = $("quizScreen");
        if (quizScreen) quizScreen.hidden = false;
    } catch (error) {
        if (questionElement) questionElement.textContent = "Unable to load the question.";
        showMessage(error.message, "error");
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
    if (answered || gameOver || selectedAnswer === null) {
        if (selectedAnswer === null) showMessage("Please select an answer first.", "error");
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
        setText("score", score);

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

        if (data.game_over) {
            gameOver = true;
            showResults(data.message, data.winnings, data.score);
            return;
        }

        const nextButton = $("nextQuestionBtn");
        if (nextButton) nextButton.hidden = false;

        setText("winnings", formatRupees(data.winnings));
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
    setText("finalWinnings", formatRupees(winnings));

    syncLifelines([]);
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
            const optionsContainer = $("options");
            if (optionsContainer) {
                const remaining = new Set(data.options);
                document.querySelectorAll(".option-btn").forEach((button) => {
                    const option = button.textContent.replace(/^[A-D]\.\s*/, "");
                    if (!remaining.has(option)) {
                        button.disabled = true;
                        button.classList.add("eliminated");
                    }
                });
            }
            showMessage("50:50 used. Two incorrect options have been removed.");
        } else if (name === "audience_poll") {
            const poll = Object.entries(data.poll)
                .map(([option, percentage]) => `${option}: ${percentage}%`)
                .join("\n");
            showMessage(`Simulated Audience Poll:\n${poll}`);
        } else if (name === "phone_friend") {
            showMessage(
                `Your friend suggests: ${data.answer}\n` +
                `${data.confidence_percentage}% confident.\n${data.reason}`
            );
        } else if (name === "ask_expert") {
            showMessage(`Ask the Expert (simulation): ${data.hint}`);
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

document.addEventListener("DOMContentLoaded", () => {
    const submitButton = $("submitAnswerBtn");
    if (submitButton) submitButton.addEventListener("click", submitAnswer);

    const nextButton = $("nextQuestionBtn");
    if (nextButton) nextButton.addEventListener("click", nextQuestion);

    const fiftyButton = $("fiftyFiftyBtn");
    if (fiftyButton) {
        fiftyButton.addEventListener("click", () =>
            useLifeline("fifty_fifty", "/use-fifty-fifty")
        );
    }

    const audienceButton = $("audiencePollBtn");
    if (audienceButton) {
        audienceButton.addEventListener("click", () =>
            useLifeline("audience_poll", "/use-audience-poll")
        );
    }

    const phoneButton = $("phoneFriendBtn");
    if (phoneButton) {
        phoneButton.addEventListener("click", () =>
            useLifeline("phone_friend", "/use-phone-friend")
        );
    }

    const expertButton = $("askExpertBtn");
    if (expertButton) {
        expertButton.addEventListener("click", () =>
            useLifeline("ask_expert", "/use-ask-expert")
        );
    }

    const quitButton = $("quitGameBtn");
    if (quitButton) quitButton.addEventListener("click", quitGame);

    loadQuestion();
});
