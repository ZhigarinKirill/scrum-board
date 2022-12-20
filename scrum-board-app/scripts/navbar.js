function loadNavbar() {
  $("#navbarId").html(`
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <a class="navbar-brand" href="../pages/index.html">Scrum Board</a>
    <button
      class="navbar-toggler"
      type="button"
      data-toggle="collapse"
      data-target="#navbarSupportedContent"
      aria-controls="navbarSupportedContent"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>
  
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav mr-auto">
        <li class="nav-item">
          <a id="home_page" class="nav-link" href="../pages/index.html">Home </a>
        </li>
  
        <li class="nav-item">
          <a id="task_page" class="nav-link" href="../pages/tasks.html">Board</a>
        </li>
      </ul>
      <!-- <form class="form-inline my-2 my-lg-0">
        <input
          class="form-control mr-sm-2"
          type="search"
          placeholder="Search"
          aria-label="Search"
        />
        <button class="btn btn-outline-success my-2 my-sm-0" type="submit">
          Search
        </button>
      </form> -->
      <a
        id="loginButton"
        class="btn btn-outline-primary my-2 my-sm-0"
        style="margin-right: 50px"
        href="../pages/signin.html"
      >
        Sign-In
      </a>
    </div>
  </nav>
    `)
  token = localStorage.getItem('access_token');
  console.log(token)
  if (token !== null) {
    console.log("gdagag")
    console.log($("#navbarId a#loginButton").text())
    $("#loginButton").text("Log Out");

  } else {
    $("#loginButton").text("Sign In");
  }

  $("#loginButton").on("click", (e) => {
    if ($("#navbarId a#loginButton").text().trim() === 'Log Out') {
      localStorage.removeItem('access_token');
    }
  });

}

