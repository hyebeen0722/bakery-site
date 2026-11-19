if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("arrived")
        observer.unobserve(entry.target)
      }
    }
  }, { threshold: 0.12 })

  document.querySelectorAll(".menu article").forEach(card => observer.observe(card))
}