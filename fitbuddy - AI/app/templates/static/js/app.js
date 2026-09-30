document.addEventListener(
    "DOMContentLoaded",
    function () {

        const forms =
            document.querySelectorAll("form");


        forms.forEach(
            function (form) {

                form.addEventListener(
                    "submit",
                    function () {

                        const button =
                            form.querySelector(
                                "button[type='submit']"
                            );


                        if (
                            button &&
                            !form.action.includes(
                                "delete-user"
                            )
                        ) {

                            button.disabled =
                                true;

                            button.textContent =
                                "Generating...";

                        }

                    }
                );

            }
        );

    }
);