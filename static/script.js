const subjectButtons = document.querySelectorAll(".subject-button");

const selectedSubjectText = document.getElementById("selected-subject");

const startButton = document.getElementById("start-button");

let selectedSubject = null;


subjectButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        subjectButtons.forEach(function (item) {
            item.classList.remove("selected");
        });

        button.classList.add("selected");

        selectedSubject = button.dataset.subject;

        selectedSubjectText.textContent =
            "Selected subject: " + selectedSubject;

        startButton.disabled = false;

    });

});


startButton.addEventListener("click", function () {

    if (selectedSubject === null) {
        return;
    }

    alert(
        "You selected " + selectedSubject +
        ". The actual quiz will be connected in our next milestone!"
    );

});