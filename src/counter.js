let count = 0;
const counterElement = document.getElementById("counter");
const incrementBtn = document.getElementById("incrementBtn");

incrementBtn.addEventListener("click", () => {
  count++;
  counterElement.textContent = count;
});
