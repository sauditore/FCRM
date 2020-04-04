/**
 * Created by amirp on 9/19/2016.
 */
$(function(){
    var i = 60;
    var b = 0;
    setInterval(function(){
        if(i==56){
            $.ajax({
                url: '/service/dc_current/',
                method: 'get',
                success:function(){

                },
                error: function(){
                    //sAlert('لطفا جهت تکمیل شارژ روتر را به مدت 1 دقیقه خاموش و سپس مجددا روشن نمایید', 10);
                }
            });
        }
        if(i<56){
            var xi = new Image();
            xi.src = 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png?a='+b;
            xi.onload = function(){
                b += 1;
            };
            if(b>5){
                document.location = 'https://www.google.com/'
            }
        }
        if(i<1){
            if(b < 1){
                sAlert('لطفا جهت تکمیل شارژ روتر را به مدت 1 دقیقه خاموش و سپس مجددا روشن نمایید. در صورت عدم شارژ با واحد پشتیبانی تماس حاصل فرمایید', 10);
            }
            else {
                document.location = "/";
            }
            $('#hHere').removeClass('hidden');
            $('#hWait').remove();
        }
        $('#dTimer').html(i);
        i-=1;
    }, 1000);
});

