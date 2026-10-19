
const questionElement = document.getElementById("question");
const optionsElement = document.getElementById("options");
const submitButton = document.getElementById("submit-button");
const nextButton = document.getElementById("next-button");
const feedbackElement = document.getElementById("feedback");
const scoreElement = document.getElementById("score");
const counterElement = document.getElementById("question-counter");
const homeButton = document.getElementById("home-button");

const fiftyFiftyButton = document.getElementById("fifty-fifty-button");
const audiencePollButton = document.getElementById("audience-poll-button");
const audiencePollResults = document.getElementById("audience-poll-results");
const audiencePollBars = document.getElementById("audience-poll-bars");

const quizScreen = document.getElementById("quiz-screen");
const resultScreen = document.getElementById("result-screen");
const finalScoreElement = document.getElementById("final-score");
const finalMessageElement = document.getElementById("final-message");
const playAgainButton = document.getElementById("play-again-button");
const resultHomeButton = document.getElementById("result-home-button");

let currentIndex = 0;
let totalQuestions = 5;
let score = 0;
let selectedAnswer = null;
let answerSubmitted = false;

let fiftyFiftyUsed = false;
let audiencePollUsed = false;

async function loadQuestion() {
    selectedAnswer = null;
    answerSubmitted = false;

    submitButton.disabled = true;
    submitButton.hidden = false;
    submitButton.textContent = "SUBMIT ANSWER";

    nextButton.hidden = true;
    nextButton.textContent = "NEXT QUESTION";

    feedbackElement.textContent = "";
    feedbackElement.className = "feedback";
    optionsElement.innerHTML = "";

    audiencePollResults.hidden = true;
    audiencePollBars.innerHTML = "";

    fiftyFiftyButton.disabled = fiftyFiftyUsed;
    fiftyFiftyButton.textContent = fiftyFiftyUsed
        ? "50:50 USED"
        : "50:50";

    audiencePollButton.disabled = audiencePollUsed;
    audiencePollButton.textContent = audiencePollUsed
        ? "POLL USED"
        : "AUDIENCE POLL";

    counterElement.textContent =
        "Question " + (currentIndex + 1) + " of " + totalQuestions;

    scoreElement.textContent = "Score: " + score;
    questionElement.textContent = "Loading your question...";

    try {
        const response = await fetch("/get-question", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                subject: subject,
                index: currentIndex
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not load question.");
        }

        totalQuestions = data.total;

        counterElement.textContent =
            "Question " + (currentIndex + 1) + " of " + totalQuestions;

        questionElement.textContent = data.question;

        data.options.forEach(function (option, index) {
            const button = document.createElement("button");

            button.type = "button";
            button.className = "answer-option";
            button.textContent =
                String.fromCharCode(65 + index) + ". " + option;

            button.addEventListener("click", function () {
                if (answerSubmitted) return;

                selectedAnswer = option;

                document.querySelectorAll(".answer-option").forEach(
                    function (item) {
                        item.classList.remove("selected");
                    }
                );

                button.classList.add("selected");
                submitButton.disabled = false;
            });

            optionsElement.appendChild(button);
        });
    } catch (error) {
        questionElement.textContent = error.message;
    }
}

// 50:50 lifeline: remove two incorrect options.
fiftyFiftyButton.addEventListener("click", async function () {
    if (fiftyFiftyUsed || answerSubmitted) return;

    fiftyFiftyButton.disabled = true;

    try {
        const response = await fetch("/use-fifty-fifty", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                subject: subject,
                index: currentIndex
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not use 50:50.");
        }

        fiftyFiftyUsed = true;

        const remainingOptions = data.options;

        document.querySelectorAll(".answer-option").forEach(
            function (button) {
                const optionText = button.textContent.substring(3);

                if (!remainingOptions.includes(optionText)) {
                    button.remove();
                }
            }
        );

        if (
            selectedAnswer !== null &&
            !remainingOptions.includes(selectedAnswer)
        ) {
            selectedAnswer = null;
            submitButton.disabled = true;

            document.querySelectorAll(".answer-option").forEach(
                function (button) {
                    button.classList.remove("selected");
                }
            );
        }

        fiftyFiftyButton.textContent = "50:50 USED";
        fiftyFiftyButton.disabled = true;

    } catch (error) {
        fiftyFiftyButton.disabled = false;
        feedbackElement.textContent = error.message;
        feedbackElement.className = "feedback incorrect";
    }
});

// Audience Poll: display simulated votes for the current options.
audiencePollButton.addEventListener("click", function () {
    if (audiencePollUsed || answerSubmitted) return;

    const optionButtons = Array.from(
        document.querySelectorAll(".answer-option")
    );

    if (optionButtons.length === 0) return;

    audiencePollUsed = true;
    audiencePollButton.disabled = true;
    audiencePollButton.textContent = "POLL USED";

    // Generate random simulated percentages that total 100%.
    const randomWeights = optionButtons.map(function () {
        return Math.random() + 0.1;
    });

    const totalWeight = randomWeights.reduce(function (sum, weight) {
        return sum + weight;
    }, 0);

    const percentages = randomWeights.map(function (weight) {
        return Math.floor((weight / totalWeight) * 100);
    });

    // Adjust the last percentage so the total is exactly 100%.
    const percentageTotal = percentages.reduce(function (sum, value) {
        return sum + value;
    }, 0);

    percentages[percentages.length - 1] += 100 - percentageTotal;

    audiencePollBars.innerHTML = "";

    optionButtons.forEach(function (button, index) {
        const optionLabel = button.textContent;
        const percentage = percentages[index];

        const pollRow = document.createElement("div");
        pollRow.className = "poll-row";

        const label = document.createElement("div");
        label.className = "poll-label";
        label.textContent = optionLabel;

        const barBackground = document.createElement("div");
        barBackground.className = "poll-bar-background";

        const bar = document.createElement("div");
        bar.className = "poll-bar";
        bar.style.width = percentage + "%";

        barBackground.appendChild(bar);

        const percentLabel = document.createElement("div");
        percentLabel.className = "poll-percentage";
        percentLabel.textContent = percentage + "%";

        pollRow.appendChild(label);
        pollRow.appendChild(barBackground);
        pollRow.appendChild(percentLabel);

        audiencePollBars.appendChild(pollRow);
    });

    audiencePollResults.hidden = false;
});

// Submit the selected answer.
submitButton.addEventListener("click", async function () {
    if (selectedAnswer === null || answerSubmitted) return;

    submitButton.disabled = true;
    answerSubmitted = true;

    fiftyFiftyButton.disabled = true;
    audiencePollButton.disabled = true;

    try {
        const response = await fetch("/check-answer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                subject: subject,
                index: currentIndex,
                answer: selectedAnswer
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not check answer.");
        }

        if (data.correct) {
            score++;

            feedbackElement.textContent =
                "Correct! " + data.explanation;

            feedbackElement.className = "feedback correct";
        } else {
            feedbackElement.textContent =
                "Incorrect. Correct answer: " +
                data.correct_answer + ". " + data.explanation;

            feedbackElement.className = "feedback incorrect";
        }

        scoreElement.textContent = "Score: " + score;
        submitButton.hidden = true;

        nextButton.textContent =
            currentIndex < totalQuestions - 1
                ? "NEXT QUESTION"
                : "VIEW RESULTS";

        nextButton.hidden = false;

    } catch (error) {
        answerSubmitted = false;
        submitButton.disabled = selectedAnswer === null;
        fiftyFiftyButton.disabled = fiftyFiftyUsed;
        audiencePollButton.disabled = audiencePollUsed;

        feedbackElement.textContent = error.message;
        feedbackElement.className = "feedback incorrect";
    }
});

// Move to the next question.
nextButton.addEventListener("click", function () {
    if (!answerSubmitted) return;

    if (currentIndex < totalQuestions - 1) {
        currentIndex++;
        loadQuestion();
    } else {
        showResults();
    }
});

// Display the final score.
function showResults() {
    quizScreen.hidden = true;
    resultScreen.hidden = false;

    finalScoreElement.textContent =
        "You answered " + score + " out of " +
        totalQuestions + " questions correctly.";

    if (score === totalQuestions) {
        finalMessageElement.textContent =
            "Excellent! You answered every question correctly!";
    } else if (score >= 3) {
        finalMessageElement.textContent =
            "Good work! Keep practising to improve your score.";
    } else {
        finalMessageElement.textContent =
            "Keep learning and try again. You can improve!";
    }
}

// Start a new game.
function restartQuiz() {
    window.location.href =
        "/quiz?subject=" + encodeURIComponent(subject);
}

homeButton.addEventListener("click", function () {
    window.location.href = "/";
});

resultHomeButton.addEventListener("click", function () {
    window.location.href = "/";
});

playAgainButton.addEventListener("click", restartQuiz);

// Load the first question.
loadQuestion();
