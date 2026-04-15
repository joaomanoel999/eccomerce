

document.querySelector("form").addEventListener("submit",function(e){

let email = document.getElementById("email").value;
let senha = document.getElementById("senha").value;

if(email === "" || senha === ""){

alert("Preencha todos os campos");
e.preventDefault();
}
});

