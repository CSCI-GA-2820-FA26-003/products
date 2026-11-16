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

// Story #43: Retrieve a product by ID
$("#retrieve-btn").click(function (event) {
    event.preventDefault();

    let product_id = $("#product_id").val();

    if (!product_id) {
        flash_message("Please enter a Product ID");
        return;
    }

    $.ajax({
        type: "GET",
        url: "/products/" + product_id,
        success: function (res) {
            update_form_data(res);
            flash_message("Product retrieved successfully");
        },
        error: function (xhr) {
            clear_form_data();

            if (xhr.status === 404) {
                flash_message("Product not found");
            } else {
                flash_message("Error retrieving product");
            }
        }
    });
});

   }); // end $(function)
