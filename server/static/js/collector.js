function makeLink() {
  let countryCodeInput = document.getElementById("countryCode");
  let number_input = document.getElementById("number");
  let message_input = document.getElementById("message");
  let countryCode = countryCodeInput.value.trim()
  let number = number_input.value.trim().replace(/\D/g,'');
  let message = message_input.value.trim();
  console.log(countryCode, number, message)
  let wa_link = `https://web.whatsapp.com/send?phone=${countryCode}${number}&text=${message}&app_absent=1`
  console.log(wa_link)
  document.getElementById('wa_link').innerHTML = wa_link
  document.getElementById('wa_link').href = wa_link
}