$('#signinButton').on('click', (e) => {
    var username = $('#usernameInput').val();

    var password = $('#passwordInput').val();

    $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        data: JSON.stringify({ "username": username, "password": password }),
        url: 'http://127.0.0.1:5000/api/users/login',
        success: function (data) {
            access_token = data.access_token;
            console.log('data: ', access_token);
            localStorage.setItem('access_token', access_token);
            $(location).attr('href', 'tasks.html');
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert("INVALID USERNAME OR PASSWORD");
            $('#usernameInput').val("");
            $('#passwordInput').val("");
        }
    });
})

$('#signupButton').on('click', (e) => {
    var username = $('#usernameInput').val();

    var email = $('#emailInput').val();
    var password = $('#passwordInput').val();
    var confirmationPassword = $('#passwordConfirmationInput').val();
    if (password !== confirmationPassword) {
        alert("PASSWORDS MUST MATCH");
        $('#usernameInput').val("");
        $('#passwordInput').val("");
        $('#emailInput').val("");
        $('#passwordConfirmationInput').val("");
        return;
    }

    $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        data: JSON.stringify({ "username": username, "email": email, "password": password }),
        url: 'http://127.0.0.1:5000/api/users/register',
        success: function (_) {
            $(location).attr('href', 'signin.html');
        }
    });
})
