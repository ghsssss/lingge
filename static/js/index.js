
var can_load =true;
function loadmore() {
    can_load =false;
    if (q != null) {
        url = '/load_more?q=' + q + '&p=' + p + '&ord=' + ord+'&t='+Date.now();
    } else {

        url = '/load_more?tid=' + tid + '&p=' + p + '&ord=' + ord+'&t='+Date.now();;
    }
    $.get(url, function (data) {

        if (data != 'None') {
            $('#loaderx').append(data);
            p = p + 1;
            can_load=true;

        } else {
            isend = true;
        }
    });

}



function ordf(idx) {
    isend = false;

    $('.ord_active').removeClass('ord_active');

    $('.section3 .sort li a:eq(' + idx + ')').addClass('ord_active');

    $("#loaderx").empty();
    ord = idx;
    p = 1;
    loadmore();
}

$(function () {


    W = window.innerWidth;
    H = window.screen.height;

    if ((!navigator.userAgent.match(/Mobile/i) ) && (W >= H)) {

        W = H * (750 / 1342);
        $("html").css("font-size", W * 0.1 + 'px');

        $('html, body').animate({scrollTop: 0});
    }


    else {

        $("html").css("font-size", W * 0.1 + 'px');
        $('html, body').animate({scrollTop: 0});

    }


    var mySwiper1 = new Swiper('#header1', {

        initialSlide: tid - 1,
        freeMode: true,
        slidesPerView: 'auto'

    });

    $("#header1 .swiper-slide:eq(" + (tid - 1) + ")>a").attr("class", "effact");
    $(".scollTop").click(function () {

            $('html, body').animate({scrollTop: 0}, 'slow');
            $(".tabs").fadeIn();
        }
    );


    var swiper = new Swiper('.Carousel .swiper-container', {
        pagination: '.swiper-pagination',
        paginationClickable: true,

    });


    loadmore();
    $(window).scroll(function () {


        if ($(document).scrollTop() >= 160) {
            $(".scollTop").show();
        } else {
            $(".scollTop").hide();
        }

        if ($(document).scrollTop() + $(window).height() >= $(document).height()*0.5 && isend == false &&can_load==true) {

            loadmore();

        }
    });

    $('body').on('moveend', function (e) {
        y = e.startY - e.pageY;
        if (y > 15) {
            $(".tabs").fadeOut();

        }        // move is complete!
        else if (y < -15) {
            $(".tabs").fadeIn();

        }
        if ($(document).scrollTop() <= 27) {
            $(".tabs").fadeIn();
        }
    });

})
;


wx.ready(function () {
    // 在这里调用 API
    // 在这里调用 API

    wx.onMenuShareTimeline({
        title: '灵阁优惠券', // 分享标题
        link: link, // 分享链接
        imgUrl: 'http://lingge.accdo.com/static/img/wx.jpg', // 分享图标
        success: function () {

            // 用户确认分享后执行的回调函数
        },
        cancel: function () {

            // 用户取消分享后执行的回调函数
        }
    });
    wx.onMenuShareAppMessage({
        title: '灵阁优惠券', // 分享标题
        desc: '精选内部优惠券！赶快来领取', // 分享描述
        link: link, // 分享链接
        imgUrl: 'http://lingge.accdo.com/static/img/wx.jpg', // 分享图标
        type: 'link', // 分享类型,music、video或link，不填默认为link
        dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
        success: function () {

            // 用户确认分享后执行的回调函数
        },
        cancel: function () {

            // 用户取消分享后执行的回调函数
        }
    });
});