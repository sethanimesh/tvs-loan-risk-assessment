(function($){
    function floatLabel(inputType){
        $(inputType).each(function(){
            var $this = $(this);
            // on focus add class active to label
            $this.focus(function(){
                $this.next('label').addClass("active");
            });
            // on blur check field and remove class if needed
            $this.blur(function(){
                if($this.val() === ''){
                    $this.next('label').removeClass("active");
                } else {
                    $this.next('label').addClass("active");
                }
            });
            // check if there's a value in the input on load
            if($this.val() !== '') {
                $this.next('label').addClass("active");
            }
        });
    }
    // apply floatLabel to the input fields
    floatLabel(".floatLabel");
})(jQuery);