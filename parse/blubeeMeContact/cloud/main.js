Parse.Cloud.define("sendBlubeeEmail", function(request, response){


    var Mandrill = require("mandrill");
    Mandrill.initialize("--MandrillKey---");

    var name = request.params.mName;
    var email = request.params.mEmail;
    var message = request.params.mMessage;

    Mandrill.sendEmail({

        message: {
            key: "message key",
            to: [
                {email:""},
                {name:""}
            ],
            from_email: email,
            from_name: name,
            subject: "",
            text: message
        },
        async: true

    }, { success: function (httpResponse) {
        console.log(httpResponse);
        response.success("Email Sent!");
    }, error: function (httpResponse) {
        console.log(httpResponse);
        response.error("Something went wrong!? : "+httpResponse.status+" : "+httpResponse.text);
    }
    });
});