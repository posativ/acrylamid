 $(document).ready(function () {
        var route;
        var m = document.getElementById('mainMenu').getElementsByTagName('li');

        var len = m.length;
        for (var i = 0; i < len; i++) {

            route = '{{ env.route }}';

            if (route.toLowerCase() == '/' && m[i].children[0].innerHTML.toLowerCase() == 'home') {
                $(m[i]).addClass('active');
                break;
            }

            if (route.toLowerCase().indexOf(m[i].children[0].innerHTML.toLowerCase()) >= 0) {
                $(m[i]).addClass('active');
                break;
            }
            $(m[i]).removeClass('active');
        }
    });