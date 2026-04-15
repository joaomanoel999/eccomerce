

function updateTotal(){

let items = document.querySelectorAll(".cart-item");
let total = 0;

items.forEach(item=>{

let price = parseFloat(item.dataset.price);
let qty = parseInt(item.querySelector(".qty").textContent);

total += price * qty;

});

document.getElementById("total").innerText =
"Total: R$ " + total.toLocaleString("pt-BR");

}

function changeQty(btn,value){

let qtyElement = btn.parentElement.querySelector(".qty");
let qty = parseInt(qtyElement.textContent);

qty += value;

if(qty < 1) qty = 1;

qtyElement.textContent = qty;

updateTotal();

}

function removeItem(btn){

btn.closest(".cart-item").remove();

updateTotal();

}

updateTotal();
