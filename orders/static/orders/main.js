$(document).ready(function() {

    retrieve_saved_cart()

    if (window.location.href.indexOf("cart") > -1) {
    
      load_cart()
    }

    if (window.location.href.indexOf("view-orders") > -1){
      order_list_functionality()
    }
  });

function order_list_functionality(){
  onRowClick("orders_table", function (row){
    var id = row.getElementsByTagName("td")[0].innerHTML;
    var csrftoken = getCookie('csrftoken');
    //send get request to see if user has superuser permissions
    var user_is_super = check_user_super();
    if ( user_is_super && row.classList.contains("mark-as-complete") ){
      var r = confirm("Would you like to mark order "+id+" as delivered?");
      if (r == true) {
        $.ajax({
            url : "/mark_order_as_delivered" , // the endpoint
            type : "POST", // http method
            data : { id : id, csrfmiddlewaretoken: csrftoken}, // data sent with the post request

            // handle a successful response
            success : function(json) {
                //make the row green
                row.classList.remove("table-danger");
                row.classList.add("table-success")
            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                //have this as another toast
                console.log("the server said no lol")
            }
        }); //make ajax post request
      }
    }

  });
}

function check_user_super(){
  var return_value;
  $.ajax({
       url: "check_superuser",
       type: 'GET',
       success: function(res) {
            console.log("we got back from the server the value ---> "+res)
            if (res == "True"){
              console.log("assigned true")
              return_value = true;
            }else{
              return_value = false;
            }
        },
        async: false
  });
  return return_value
}

function add_to_cart(info) {
  display_notif("add to cart", info);

  let cart = JSON.parse(localStorage.getItem("cart")) || [];


  let existing = cart.find(item => item.item_description === info.item_description);
  if (existing) {
      existing.qty += 1;
  } else {
      info.qty = 1; 
      cart.push(info);
  }

  localStorage.setItem('cart', JSON.stringify(cart));
}




function display_notif(type, info="No info provided"){
  //the different types of toasts are success, warning ... info and error
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": false,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "70",
    "hideDuration": "1000",
    "timeOut": "2000",
    "extendedTimeOut": "500",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
  switch (type){
    case "add to cart":
      toastr.success(info.item_description + ': Rs.' + info.price, 'Added to Cart');
      break;
    case "remove from cart":
      toastr.warning("Successfully removed "+info+ " from cart");
      break;
    case "new order":
      toastr.success("Order successfully placed");
      break;
  }

}


// Function to load the cart
function load_cart() {
  var table = document.getElementById('cart_body');
  if (!table) return;

  table.innerHTML = "";


  var cart = JSON.parse(localStorage.getItem("cart")) || [];
  var total = 0;

  if (cart.length > 0) {
      for (let i = 0; i < cart.length; i++) {
          var row = table.insertRow(-1);
          var item_number = row.insertCell(0);
          var item_description = row.insertCell(1);
          var item_price = row.insertCell(2);
          var item_qty = row.insertCell(3);
          var item_action = row.insertCell(4);

          item_number.innerHTML = String(i + 1);
          item_description.innerHTML = cart[i].item_description;
          item_price.innerHTML = "₹" + cart[i].price;
          item_action.innerHTML =  `
  <button class="btn btn-danger btn-sm delete-btn" data-index="${i}">🗑️</button>
`;

          // ✅ Quantity Picker
          item_qty.innerHTML = `
              <input type="number" min="1" value="${cart[i].qty}" data-index="${i}" class="qty-input" style="width: 60px;">
          `;

          total += parseFloat(cart[i].price) * cart[i].qty;
      }

      total = Math.round(total * 100) / 100;
      localStorage.setItem('total_price', total);
      document.getElementById('total').innerHTML = "₹" + total;
      document.getElementById('price').value = total;

      // ✅ Add real-time quantity update
      document.querySelectorAll('.qty-input').forEach(input => {
          input.addEventListener('change', function () {
              let index = this.getAttribute('data-index');
              let newQty = parseInt(this.value);

              if (newQty < 1) {
                  alert("Quantity must be at least 1");
                  this.value = 1;
                  newQty = 1;
              }

              cart[index].qty = newQty;
              localStorage.setItem("cart", JSON.stringify(cart));
              load_cart(); // reload UI and total
          });
      });
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const index = parseInt(this.getAttribute('data-index'));
            let cart = JSON.parse(localStorage.getItem("cart")) || [];
            const item = cart[index];
    
            const confirmDelete = confirm(`Remove "${item.item_description}" from cart?`);
            if (confirmDelete) {
                cart.splice(index, 1);
                localStorage.setItem("cart", JSON.stringify(cart));
                display_notif("remove from cart", item.item_description);
                load_cart(); // refresh
            }
        });
    });

    
  } else {
      display_empty_cart();
  }
}
     

// Execute only when DOM is ready
$(document).ready(function() {
  retrieve_saved_cart();

  if (window.location.href.indexOf("cart") > -1) {
      load_cart();
  }

  if (window.location.href.indexOf("view-orders") > -1) {
      order_list_functionality();
  }
});

// Function to display empty cart message
function display_empty_cart() {
  var table = document.getElementById('cart_body');
  if (table) {
      table.innerHTML = "";
  }
  document.getElementById('total').innerHTML = "";
  document.getElementById('cart_heading').innerHTML = "Cart is empty!";
  document.getElementById("checkout_button").disabled = true;
}

function format_toppings(topping_choices){
  var toppings = ""
  var arrayLength = topping_choices.length;
  for (var i = 0; i < arrayLength; i++) {
      if (i == 0){
        //first iteration
        toppings += topping_choices[i]
      }else{
        toppings += " + "
        toppings += topping_choices[i]
      }
  }
  return toppings
}

function pizza_toppings(number_of_toppings, type_of_pizza, price){
  var last_valid_selection = null;

  $('#toppings_label')[0].innerHTML = "Choose "+ String(number_of_toppings) +" topping(s) here"
  $('#select_toppings').change(function(event) {
    console.log($(this).val().length)
    console.log(number_of_toppings)
    if ($(this).val().length > number_of_toppings) {

      $(this).val(last_valid_selection);
    } else {
      last_valid_selection = $(this).val();
    }
  }); //this is what restircts the user from choosing more than they are paying fpr

  $('#toppings_modal').modal('show'); //show the modal
  $("#submit_toppings").click(function(){
    var topping_choices = $('#select_toppings').val();
    //console.log("TOPping choices are "+topping_choices[0])

    $('#toppings_modal').modal('toggle'); //hide the modal
    var info={
      "item_description": type_of_pizza + " pizza with "+ format_toppings(topping_choices),
      "price":price
    }
    add_to_cart(info)

  });
};

function close_modal(){
  $('#toppings_modal').modal('hide');
  $('#toppings_modal').modal('dispose');
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;} 
function display_empty_cart(){
  var table = document.getElementById('cart_body');
  table.innerHTML = ""; //clear the table
  document.getElementById('total').innerHTML = ""
  document.getElementById('cart_heading').innerHTML = "Cart is empty!"
  document.getElementById("checkout_button").disabled = true;

}

function clear_cart(){
  localStorage.removeItem("cart"); //Clear the cart
  localStorage.removeItem("total_price"); //clear the price
  //remove the elements from the page
  display_empty_cart();
}




function logout(){
  var current_cart = localStorage.getItem("cart")
  var csrftoken = getCookie('csrftoken');
  $.ajax({
      url : "/save_cart" , // the endpoint
      type : "POST", // http method
      data : { cart : current_cart, csrfmiddlewaretoken: csrftoken }, // data sent with the post request

      // handle a successful response
      success : function(json) {
        //clear the local storage
        localStorage.removeItem("cart"); //Clear the cart
        localStorage.setItem('cart_retrieved', false);
        window.location.href = "/logout";
      },

      // handle a non-successful response
      error : function(xhr,errmsg,err) {
          //have this as another toast
          console.log("the server said no lol")

      }
  });

}

function retrieve_saved_cart(){
  if (localStorage.getItem("cart_retrieved") !== "true"){
    $.ajax({
         url: "retrieve_saved_cart",
         type: 'GET',
         success: function(res) {
              localStorage.setItem('cart_retrieved', true);
              localStorage.setItem("cart", res)
          }
    });
    //
  }
}
function getLocation() {
  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(showPosition, showError);
  } else {
      alert("Geolocation is not supported by this browser.");
  }
}

function showPosition(position) {
  document.getElementById("latitude").value = position.coords.latitude;
  document.getElementById("longitude").value = position.coords.longitude;
  alert("Location retrieved: " + position.coords.latitude + ", " + position.coords.longitude);


  fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.coords.latitude}&lon=${position.coords.longitude}`)
  .then(response => response.json())
  .then(data => {
      if (data.display_name) {
          document.getElementById("address").value = data.display_name;
      }
  })
  .catch(error => console.error("Error fetching address:", error));
}

function showError(error) {
  alert("Error retrieving location. Please enter manually.");
}
