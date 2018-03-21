$(window).resize(function(){
    //Media queries on resize
    if ($(window).innerWidth() >= 1200){
        $('.tableheader4 h1').css("margin-left", "80px");

        if ($(window).innerWidth() >= 1200 && $(window).innerWidth() < 1300){
            marginleft = '110';
            marginleft6 = '60';
        }
        else if ($(window).innerWidth() >= 1300 && $(window).innerWidth() < 1400){
            marginleft = '90';
            marginleft6 = '50';
        }
        else if ($(window).innerWidth() >= 1400 && $(window).innerWidth() < 1500){
            marginleft = '80';  
            marginleft6 = '40';     
        }
        else if ($(window).innerWidth() >= 1500 && $(window).innerWidth() < 1600){
            marginleft = '60';
            marginleft6 = '30';
        }
        else if ($(window).innerWidth() >= 1600 && $(window).innerWidth() < 1700){
            marginleft = '45';
            marginleft6 = '20';
        }
        else if ($(window).innerWidth() >= 1700 && $(window).innerWidth() < 1800){
            marginleft = '30';
            marginleft6 = '10';
        }
        else if ($(window).innerWidth() >= 1800){
            marginleft = '0';
            marginleft6 = '0';
        }

        var appendedstring = '<th class="tableheader3" style="width: 17.7%;"><p style="padding-left: 0; margin: 16px 0 0 ' + marginleft + 'px; color: rgb(41,144,216);"><strong class="item"><span>Players Alive: </span></strong><em>{{ct_alive_count}}/{{ct_player_count}}</em></p></th>';

        var appendedstring2 = '<th class="tableheader6" style="width: 23.8%;"><p style="padding-left: 0; margin: 16px 0 0 ' + marginleft6 + 'px; color: rgb(216,144,41);"><strong class="item"><span> Players Alive: </span></strong><em>{{t_alive_count}}/{{t_player_count}}</em></p></th>'

        $('.scoreboard-header').empty();
        $('.scoreboard-header').append('<th class="tableheader1" style="width: 14%;"></th>');           
        $('.scoreboard-header').append('<th class="tableheader2" style="width: 16%; padding-right: 4px;"><h1 style="margin: 0"> <span id="ct-title" class="ct-wins">{{scoreboard.teams.3}}</span></h1></th>');
        $('.scoreboard-header').append(appendedstring);
        $('.scoreboard-header').append('<th class="tableheader4" style="width: 20%;"><h1 style="margin: 0 0 0 80px;"> <span id="ct-round-wins" class="ct-wins">{{ct_round_wins}}</span> : <span id="t-round-wins" class="t-wins">{{t_round_wins}}</span></h1></th>');
        $('.scoreboard-header').append('<th class="tableheader5" style="width: 8.5%; padding-right: 4px;"><h1 style="margin: 0"> <span id="t-title" class="t-wins">{{scoreboard.teams.2}}</span></h1></th>');
        $('.scoreboard-header').append(appendedstring2);

        if ($(window).innerWidth() >= 1800){
            $('.tableheader3 p').css("margin-left", "0");
            $('.tableheader6 p').css("margin-left", "0");
        }
    }    

    if($(window).innerWidth() >= 1500){
        $('.tableheader4 h1').css("margin-left", "0");
    }

    if ($(window).innerWidth() > 1280) {
        if($('.left-head-ct').length == 0){
            $('.ct-head-row').prepend('<th class="left-head-ct"></th>');
            $('.ct-player').prepend('<td class="left-col-ct"></td>');
            $('.t-head-row').prepend('<th class="left-head-t"></th>');
            $('.t-player').prepend('<td class="left-col-t"></td>');
        }
    } 

    if ($(window).innerWidth() <= 1280) {
        $('.left-head-ct').remove();
        $('.left-col-ct').remove();
        $('.left-head-t').remove();
        $('.left-col-t').remove();
    } 

    if ($(window).innerWidth() <= 1199) {
        if($('.tableheader1').length != 0)
        {
            $('.tableheader1').remove();
            $('.tableheader2').css("width", "50%");
            $('.tableheader2').css("padding-top", "12px");
            $('.tableheader2').css("padding-right", "35px");
            $('.tableheader2').append("<p style='margin:0; color: rgb(41,144,216);'><strong class='item'><span>Players Alive: </span></strong><em>{{ct_alive_count}}/{{ct_player_count}}</em></p>");
            $('.tableheader3').remove();
            $('.tableheader4').css("width", "25%");
            $('.tableheader4 h1').css("margin-left", "0");
            $('.tableheader4').css("padding-bottom", "18px");
            $('.tableheader5').css("width", "25%");
            $('.tableheader5').css("padding-top", "12px");
            $('.tableheader5').css("padding-left", "0");
            $('.tableheader5').append('<p style="margin: 0; color: rgb(216,144,41);"><strong class="item"><span> Players Alive: </span></strong><em>{{t_alive_count}}/{{t_player_count}}</em></p>');
            $('.tableheader6').remove();
        }

    } 

    if ($(window).innerWidth() <= 680) {
        $('.tableheader2').css("width", "50%");
        $('.tableheader4').css("width", "22%");
        $('.tableheader4 h1').css("margin-left", "0");
        $('.tableheader5').css("width", "28%");
        $('.ct-name-head').css("padding-left", "4%");
        $('.t-name-head').css("padding-left", "4%");
        $('.ct-name').css("padding-left", "4%");
        $('.t-name').css("padding-left", "4%");
    } 
});