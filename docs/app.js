/**
 * QuantSynthica Institutional Documentation Portal JavaScript
 * Supports: Search filter, Tab switching, Copy to clipboard, Scroll-spy
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Copy to Clipboard Functionality
  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const codeBlock = btn.closest(".code-block-wrapper").querySelector("pre code");
      if (!codeBlock) return;

      const text = codeBlock.innerText;
      navigator.clipboard.writeText(text).then(() => {
        const originalHtml = btn.innerHTML;
        btn.classList.add("copied");
        btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!`;

        setTimeout(() => {
          btn.classList.remove("copied");
          btn.innerHTML = originalHtml;
        }, 2000);
      });
    });
  });

  // 2. Code Block Language Tabs Switcher
  document.querySelectorAll(".code-block-wrapper").forEach((wrapper) => {
    const tabs = wrapper.querySelectorAll(".code-tab");
    const preBlocks = wrapper.querySelectorAll("pre");

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        preBlocks.forEach((p) => (p.style.display = "none"));

        tab.classList.add("active");
        if (preBlocks[index]) {
          preBlocks[index].style.display = "block";
        }
      });
    });
  });

  // 3. Instant Search Filtering
  const searchInput = document.getElementById("search-input");
  const endpointCards = document.querySelectorAll(".endpoint-card");
  const navItems = document.querySelectorAll(".nav-item");

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();

      endpointCards.forEach((card) => {
        const text = card.innerText.toLowerCase();
        if (!query || text.includes(query)) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });

      navItems.forEach((nav) => {
        const text = nav.innerText.toLowerCase();
        if (!query || text.includes(query)) {
          nav.style.display = "flex";
        } else {
          nav.style.display = "none";
        }
      });
    });

    // Keyboard shortcut (Ctrl+K or / to focus search)
    window.addEventListener("keydown", (e) => {
      if ((e.ctrlKey && e.key === "k") || (e.key === "/" && document.activeElement !== searchInput)) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });
  }

  // 4. Scroll-spy for Sidebar active links
  const sections = document.querySelectorAll("section.doc-section");
  window.addEventListener("scroll", () => {
    let current = "";
    const scrollPosition = window.pageYOffset + 120;

    sections.forEach((section) => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        current = section.getAttribute("id");
      }
    });

    navItems.forEach((item) => {
      item.classList.remove("active");
      if (current && item.getAttribute("href") === `#${current}`) {
        item.classList.add("active");
      }
    });
  });
});
