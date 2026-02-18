const wish = document.querySelector(".wish");
const audio = document.getElementById("wishAudio");

if (wish && audio) {
  const start = () => {
    audio.volume = 0.6;
    audio.play().catch(() => {});
  };

  const stop = () => {
    audio.pause();
    audio.currentTime = 0;
  };

  wish.addEventListener("mouseenter", start);
  wish.addEventListener("mouseleave", stop);
  wish.addEventListener("touchstart", start, { passive: true });
  wish.addEventListener("touchend", stop);
}
