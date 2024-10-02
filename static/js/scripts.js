(function($){
    function floatLabel(inputType){
        $(inputType).each(function(){
            var $this = $(this);
            $this.focus(function(){
                $this.next('label').addClass("active");
            });
            $this.blur(function(){
                if($this.val() === ''){
                    $this.next('label').removeClass("active");
                } else {
                    $this.next('label').addClass("active");
                }
            });
            if($this.val() !== '') {
                $this.next('label').addClass("active");
            }
        });
    }
    floatLabel(".floatLabel");
})(jQuery);