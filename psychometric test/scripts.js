const questions = [
    {
        question: "When making a financial decision, I carefully evaluate the long-term consequences before acting.",
        optionA: { text: "I usually make decisions on impulse.", score: 1 },
        optionB: { text: "I sometimes evaluate the long-term, but not always.", score: 2 },
        optionC: { text: "I often consider long-term consequences, but short-term needs usually take priority.", score: 3 },
        optionD: { text: "I always evaluate the long-term impacts before making any financial decision.", score: 4 }
    },
    {
        question: "If I receive unexpected income, such as a bonus or gift, I use it to pay down debt before spending on anything else.",
        optionA: { text: "I use it for personal expenses or enjoyment first.", score: 1 },
        optionB: { text: "I split it between paying down debt and personal spending.", score: 2 },
        optionC: { text: "I prioritize saving it but pay a small portion toward debt.", score: 3 },
        optionD: { text: "I immediately use it to reduce my debt.", score: 4 }
    },
    {
        question: "I feel comfortable borrowing money even if I’m unsure how I will repay it.",
        optionA: { text: "I often borrow without thinking about repayment.", score: 1 },
        optionB: { text: "I sometimes borrow even if I don’t have a clear plan to repay.", score: 2 },
        optionC: { text: "I rarely borrow unless I have a repayment plan.", score: 3 },
        optionD: { text: "I never borrow unless I’m 100% certain of how I will repay it.", score: 4 }
    },
    {
        question: "When I have multiple bills to pay, I make sure to prioritize debt repayment over other expenses.",
        optionA: { text: "I prioritize non-essential expenses over debt repayment.", score: 1 },
        optionB: { text: "I often struggle with prioritizing my payments.", score: 2 },
        optionC: { text: "I try to balance debt and other expenses equally.", score: 3 },
        optionD: { text: "I always prioritize debt repayment first.", score: 4 }
    },
    {
        question: "If I encounter an unexpected financial emergency, I immediately adjust my budget to ensure loan payments are still made on time.",
        optionA: { text: "I tend to ignore the loan payments during emergencies.", score: 1 },
        optionB: { text: "I delay the loan payments until my situation stabilizes.", score: 2 },
        optionC: { text: "I adjust my budget, but sometimes I still miss payments.", score: 3 },
        optionD: { text: "I always find a way to adjust my budget and ensure payments are made.", score: 4 }
    },
    {
        question: "I often plan ahead for financial situations that could affect my ability to repay a loan.",
        optionA: { text: "I don’t usually plan for future financial challenges.", score: 1 },
        optionB: { text: "I plan ahead sometimes, but it’s not always thorough.", score: 2 },
        optionC: { text: "I generally plan ahead but occasionally overlook things.", score: 3 },
        optionD: { text: "I always create a solid financial plan for future challenges.", score: 4 }
    },
    {
        question: "How often do you seek professional or trusted advice before taking on new debt?",
        optionA: { text: "I rarely, if ever, ask for advice.", score: 1 },
        optionB: { text: "I sometimes seek advice from friends or family, but not always professionals.", score: 2 },
        optionC: { text: "I seek advice for larger debts, but not for small amounts.", score: 3 },
        optionD: { text: "I always seek advice before taking on any new debt.", score: 4 }
    },
    {
        question: "If I anticipate missing a loan payment, I contact my lender in advance to discuss options.",
        optionA: { text: "I don’t contact the lender and deal with the consequences later.", score: 1 },
        optionB: { text: "I sometimes contact my lender, but only after I’ve missed a payment.", score: 2 },
        optionC: { text: "I contact the lender occasionally, but not always in advance.", score: 3 },
        optionD: { text: "I always inform my lender in advance and try to work out an arrangement.", score: 4 }
    },
    {
        question: "When it comes to paying off a loan, I prefer to pay more than the minimum required.",
        optionA: { text: "I rarely pay more than the minimum.", score: 1 },
        optionB: { text: "I pay more than the minimum occasionally.", score: 2 },
        optionC: { text: "I often try to pay more than the minimum.", score: 3 },
        optionD: { text: "I always aim to pay more than the minimum amount due.", score: 4 }
    },
    {
        question: "I am willing to cut back on non-essential expenses to stay on track with my loan repayment.",
        optionA: { text: "I avoid cutting back on my personal expenses.", score: 1 },
        optionB: { text: "I struggle to cut back but try occasionally.", score: 2 },
        optionC: { text: "I cut back on non-essentials only when absolutely necessary.", score: 3 },
        optionD: { text: "I regularly cut back on non-essential expenses to prioritize loan repayment.", score: 4 }
    }
];


let shuffledQuestions = []

function handleQuestions() { 

    while (shuffledQuestions.length <= 9) {
        const random = questions[Math.floor(Math.random() * questions.length)]
        if (!shuffledQuestions.includes(random)) {
            shuffledQuestions.push(random)
        }
    }
}


let questionNumber = 1
let playerScore = 0  
let wrongAttempt = 0 
let indexNumber = 0 

function NextQuestion(index) {
    handleQuestions()
    const currentQuestion = shuffledQuestions[index]
    document.getElementById("question-number").innerHTML = questionNumber
    document.getElementById("display-question").innerHTML = currentQuestion.question;
    document.getElementById("option-one-label").innerHTML = currentQuestion.optionA.text;
    document.getElementById("option-two-label").innerHTML = currentQuestion.optionB.text;
    document.getElementById("option-three-label").innerHTML = currentQuestion.optionC.text;
    document.getElementById("option-four-label").innerHTML = currentQuestion.optionD.text;

}


function checkForAnswer() {
    const currentQuestion = shuffledQuestions[indexNumber];
    const options = document.getElementsByName("option");

    let selectedScore = 0;

    options.forEach((option) => {
        if (option.checked) {
            if (option.value === "optionA") selectedScore = currentQuestion.optionA.score;
            else if (option.value === "optionB") selectedScore = currentQuestion.optionB.score;
            else if (option.value === "optionC") selectedScore = currentQuestion.optionC.score;
            else if (option.value === "optionD") selectedScore = currentQuestion.optionD.score;
        }
    });

    if (options[0].checked === false && options[1].checked === false && options[2].checked === false && options[3].checked === false) {
        document.getElementById('option-modal').style.display = "flex";
    } else {
        playerScore += selectedScore;
        indexNumber++;
        setTimeout(() => {
            questionNumber++;
        }, 1000);
    }
}

function handleNextQuestion() {
    checkForAnswer() 
    unCheckRadioButtons()
    setTimeout(() => {
        if (indexNumber <= 9) {
            NextQuestion(indexNumber)
        }
        else {
            handleEndGame()
        }
        resetOptionBackground()
    }, 1000);
}

function resetOptionBackground() {
    const options = document.getElementsByName("option");
    options.forEach((option) => {
        document.getElementById(option.labels[0].id).style.backgroundColor = ""
    })
}

function unCheckRadioButtons() {
    const options = document.getElementsByName("option");
    for (let i = 0; i < options.length; i++) {
        options[i].checked = false;
    }
}

function handleEndGame() {
    let remark = null;
    let remarkColor = null;

    if (playerScore <= 15) {
        remark = "Poor financial behavior. Consider better planning.";
        remarkColor = "red";
    } else if (playerScore > 15 && playerScore <= 30) {
        remark = "Average financial behavior. Improvement is needed.";
        remarkColor = "orange";
    } else if (playerScore > 30) {
        remark = "Excellent financial behavior. You are responsible.";
        remarkColor = "green";
    }
    const playerGrade = (playerScore / 40) * 100; 

    document.getElementById('remarks').innerHTML = remark;
    document.getElementById('remarks').style.color = remarkColor;
    document.getElementById('grade-percentage').innerHTML = playerGrade.toFixed(2);
    document.getElementById('score-modal').style.display = "flex";
}

function closeScoreModal() {
    questionNumber = 1
    playerScore = 0
    wrongAttempt = 0
    indexNumber = 0
    shuffledQuestions = []
    NextQuestion(indexNumber)
    document.getElementById('score-modal').style.display = "none"
}

function closeOptionModal() {
    document.getElementById('option-modal').style.display = "none"
}