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
    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        let stock = $("#product_stock").val();

        let data = {
            "name": $("#product_name").val(),
            "description": $("#product_description").val(),
            "category": $("#product_category").val(),
            "price": $("#product_price").val(),
            "stock": stock === "" ? null : parseInt(stock, 10),
            "image_url": $("#product_image_url").val()
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/api/products",
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function (res) {
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        let product_id = $("#product_id").val().trim();
        let stock = $("#product_stock").val();

        if (product_id === "") {
            flash_message("Enter a Product ID to update.");
            return;
        }

        let data = {
            "name": $("#product_name").val(),
            "description": $("#product_description").val(),
            "category": $("#product_category").val(),
            "price": $("#product_price").val(),
            "stock": stock === "" ? null : parseInt(stock, 10),
            "image_url": $("#product_image_url").val()
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: "/api/products/" + product_id,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function (res) {
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message);
        });
    });

    // ===== Action handlers are added by their User Stories =====
    // #42 Create, #43 Read, #49 Update, #50 Delete,
    // #52 List, #53 Query, #54 Action
    function change_stock(action, method) {
        const id = $("#product_id").val().trim();
        const quantity = Number($("#product_quantity").val());
        const buttons = $("#restock-btn, #buy-btn");

        if (!/^[1-9]\d*$/.test(id)) {
            flash_message("Enter a valid Product ID.");
            return;
        }
        if (!Number.isSafeInteger(quantity) || quantity < 1) {
            flash_message("Quantity must be a positive integer.");
            return;
        }

        $("#flash_message").empty();
        buttons.prop("disabled", true);

        $.ajax({
            type: method,
            url: "/api/products/" + id + "/" + action,
            contentType: "application/json",
            data: JSON.stringify({ quantity: quantity })
        }).done(function (res) {
            update_form_data(res);
            flash_message("Success");
        }).fail(function (res) {
            const message = res.responseJSON && res.responseJSON.message;
            $("#flash_message").text(message || "Unable to update stock.");
        }).always(function () {
            buttons.prop("disabled", false);
        });
    }

    $("#restock-btn").click(function () {
        change_stock("restock", "POST");
    });

    $("#buy-btn").click(function () {
        change_stock("purchase", "PUT");
    });
    // Utility: render products into the results table
    function populate_table(products) {
        let tbody = $("#search_results tbody");
        tbody.empty();
        for (let i = 0; i < products.length; i++) {
            let p = products[i];
            tbody.append(
                `<tr>
                  <td>${p.id}</td>
                  <td>${p.name}</td>
                  <td>${p.description}</td>
                  <td>${p.category}</td>
                  <td>${p.price}</td>
                  <td>${p.stock}</td>
                  <td>${p.image_url}</td>
                </tr>`
            );
        }
    }

    // ****************************************
    // Search Products
    // ****************************************
    $("#search-btn").click(function () {
        const query = {};
        const name = $("#product_name").val().trim();
        const category = $("#product_category").val().trim();
        const price = $("#product_price").val().trim();

        if (name) {
            query.name = name;
        }
        if (category) {
            query.category = category;
        }
        if (price) {
            query.min_price = price;
            query.max_price = price;
        }

        $("#flash_message").empty();
        $.ajax({ type: "GET", url: "/api/products", data: query })
            .done(function (res) {
                populate_table(res);
                flash_message("Success");
            })
            .fail(function (res) {
                const message = res.responseJSON && res.responseJSON.message;
                flash_message(message || "Unable to search products.");
            });
    });

    // ****************************************
    // List all Products
    // ****************************************
    $("#list_products-btn").click(function () {
        $("#flash_message").empty();
        $.ajax({ type: "GET", url: "/api/products" })
            .done(function (res) {
                populate_table(res);
            })
            .fail(function (res) {
                flash_message(res.responseJSON.message);
            });
    });

}); // end $(function)