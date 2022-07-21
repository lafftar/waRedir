function makeLink() {
  let number_input = document.getElementById("number");
  let message_input = document.getElementById("message");
  let number = number_input.value.trim().replace(/\D/g,'');
  let message = message_input.value.trim();
  console.log(number, message)
  let wa_link = `https://api.whatsapp.com/send/?phone=${number}&text=${message}&app_absent=0`
  console.log(wa_link)
  document.getElementById('wa_link').innerHTML = wa_link
  document.getElementById('wa_link').href = wa_link
}