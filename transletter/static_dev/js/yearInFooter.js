const userYear = new Date().getFullYear();
const currentYearElement = document.getElementById("footerYear");
const currentYear = parseInt(currentYearElement.textContent);
const currentDate = new Date();
const year24HoursAgo = new Date(currentDate.getTime() - (24 * 60 * 60 * 1000)).getFullYear();
const isDifferentYear = currentYear !== userYear && year24HoursAgo !== userYear;

if (isDifferentYear) {
  currentYearElement.textContent = userYear;
}