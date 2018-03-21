$(document).ready(function(){
    //Initial Page Load Media queries
    if ($(window).innerWidth() >= 1200 && $(window).innerWidth() < 1800) {       
        $('.tableheader4 h1').css("margin-left", "80px");

        if ($(window).innerWidth() >= 1200 && $(window).innerWidth() < 1300){
            $('.tableheader3 p').css("margin-left", "110px");
            $('.tableheader6 p').css("margin-left", "60px");
        }
        else if ($(window).innerWidth() >= 1300 && $(window).innerWidth() < 1400){
            $('.tableheader3 p').css("margin-left", "90px");
            $('.tableheader6 p').css("margin-left", "50px");
        }
        else if ($(window).innerWidth() >= 1400 && $(window).innerWidth() < 1500){
            $('.tableheader3 p').css("margin-left", "80px");
            $('.tableheader6 p').css("margin-left", "40px");     
        }
        else if ($(window).innerWidth() >= 1500 && $(window).innerWidth() < 1600){
            $('.tableheader3 p').css("margin-left", "60px");
            $('.tableheader6 p').css("margin-left", "30px");
        }
        else if ($(window).innerWidth() >= 1600 && $(window).innerWidth() < 1700){
            $('.tableheader3 p').css("margin-left", "45px");
            $('.tableheader6 p').css("margin-left", "20px");
        }
        else if ($(window).innerWidth() >= 1700 && $(window).innerWidth() < 1800){
            $('.tableheader3 p').css("margin-left", "30px");
            $('.tableheader6 p').css("margin-left", "10px");
        }
    }

    if ($(window).innerWidth() >= 1500){
        $('.tableheader4 h1').css("margin-left", "0px");
    }    

    if ($(window).innerWidth() <= 1280) {
        $('.left-head-ct').remove();
        $('.left-col-ct').remove();
        $('.left-head-t').remove();
        $('.left-col-t').remove();
    } 

    if ($(window).innerWidth() <= 1199) {
        $('.tableheader1').remove();
        $('.tableheader2').css("width", "50%");
        $('.tableheader2').css("padding-top", "12px");
        $('.tableheader2').css("padding-right", "35px");
        $('.tableheader2').append("<p style='margin:0; color: rgb(41,144,216);'><strong class='item'><span>Players Alive: </span></strong><em>{{ct_alive_count}}/{{ct_player_count}}</em></p>");
        $('.tableheader3').remove();
        $('.tableheader4').css("width", "25%");
        $('.tableheader4').css("padding-bottom", "18px");
        $('.tableheader5').css("width", "25%");
        $('.tableheader5').css("padding-top", "12px");
        $('.tableheader5').css("padding-left", "0");
        $('.tableheader5').append('<p style="margin: 0; color: rgb(216,144,41);"><strong class="item"><span> Players Alive: </span></strong><em>{{t_alive_count}}/{{t_player_count}}</em></p>');
        $('.tableheader6').remove();
    } 

    if ($(window).innerWidth() <= 680) {
        $('.tableheader2').css("width", "50%");
        $('.tableheader4').css("width", "22%");
        $('.tableheader5').css("width", "28%");
        $('.ct-name-head').css("padding-left", "4%");
        $('.t-name-head').css("padding-left", "4%");
        $('.ct-name').css("padding-left", "4%");
        $('.t-name').css("padding-left", "4%");
    } 
});
