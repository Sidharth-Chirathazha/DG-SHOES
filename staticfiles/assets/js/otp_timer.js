document.addEventListener('DOMContentLoaded', (event) => {
    // Get the OTP expiration time from the context
    const otpExpiration = new Date(document.getElementById('otp-expiration').textContent);
    // Calculate the remaining time in seconds
    let remainingTime = (otpExpiration - new Date()) / 1000;

    // Update the timer every second
    const timerInterval = setInterval(() => {
        if (remainingTime <= 0) {
            clearInterval(timerInterval);
            document.getElementById('timer').innerHTML = "OTP expired! Please resend OTP.";
            document.getElementById('resend-btn').style.display = 'block';
        } else {
            remainingTime--;
            const minutes = Math.floor(remainingTime / 60);
            const seconds = Math.floor(remainingTime % 60);
            document.getElementById('timer').innerHTML = `Time left: ${minutes}m ${seconds}s`;
        }
    }, 1000);
});