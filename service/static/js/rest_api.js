$(function () {

       // Utility: fill the form from an API response
       function update_form_data(res) {
           $("#product_id").val(res.id);
           $("#product_name").val(res.name);
           $("#product_description").val(res.description);
           $("#product_category").val(res.category);
           $("#product_price").val(res.price);
           $("#product_stock").val(res.stock);
           $("#product_image_url").val(res.image_url);
       }

       // Utility: clear the form
       function clear_form_data() {
           $("#product_name").val("");
           $("#product_description").val("");
           $("#product_category").val("");
           $("#product_price").val("");
           $("#product_stock").val("");
           $("#product_image_url").val("");
       }

       // Utility: show a status message
       function flash_message(message) {
           $("#flash_message").empty();
           $("#flash_message").append(message);
       }

       // ===== Action handlers are added by their User Stories =====
       // #42 Create, #43 Read, #49 Update, #50 Delete,
       // #52 List, #53 Query, #54 Action

   }); // end $(function)
