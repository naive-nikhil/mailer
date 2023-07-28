const tabsContainer = document.querySelector(".tabs-container");
const tabsList = document.querySelector("ul");
const tabButtons = document.querySelectorAll("a");
const tabPanels = document.querySelectorAll(".tabs__panels > div");

tabsList.setAttribute("role", "tablist");

tabsList.querySelectorAll('li').forEach((listitem) => {
    listitem.setAttribute("role", "presentation");
});

tabButtons.forEach((tab, index) => {
    tab.setAttribute("role", "tab");
    if (index === 0){
    tab.setAttribute("aria-selected", "true");
    }else{
        tab.setAttribute("tabindex", "-1");
        tabPanels[index].setAttribute("hidden", "");
    }
});

tabPanels.forEach((panel) => {
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("tabindex", "0")
});

tabsContainer.addEventListener("click", (e) => {
    const clickedTab = e.target.closest("a")
    if (!clickedTab) return;
    e.preventDefault();

    switchTab(clickedTab);
});


function switchTab(newTab) {
    const activePanelId = newTab.getAttribute('href');
    const activePanel = tabsContainer.querySelector(activePanelId);

    tabButtons.forEach((button) => {
        button.setAttribute("aria-selected", false);
        button.setAttribute("tabindex", "-1");
    });

    tabPanels.forEach((panel) => {
        panel.setAttribute("hidden", true);
    });
    activePanel.removeAttribute("hidden");

    newTab.setAttribute("aria-selected", true)
    newTab.setAttribute("tabindex", "0");
}