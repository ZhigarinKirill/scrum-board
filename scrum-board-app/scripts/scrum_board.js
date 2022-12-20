function changeTaskStatus(taskId, status) {
  $.ajax({
    type: 'PATCH',
    dataType: 'json',
    contentType: "application/json",
    url: `http://127.0.0.1:5000/api/users/tasks/${taskId}/${status}`,
    headers: {
      "Authorization": `Bearer ${localStorage.getItem('access_token')}`
    },
    success: function () {
    }
  });
}

function addButtonActions() {
  $(".button-backlog").on("click", function () {
    if (!($(this).closest(".backlog").length > 0)) {
      $(this).parents(".input-group").appendTo(".backlog");
      var taskId = $(this).parents(".input-group").attr("id").replace(/^\D+/g, '')
      changeTaskStatus(taskId, 0);
    }
  });

  $(".button-progress").on("click", function () {
    if (!($(this).closest(".in-progress").length > 0)) {
      $(this).parents(".input-group").appendTo(".in-progress");
      var taskId = $(this).parents(".input-group").attr("id").replace(/^\D+/g, '')
      changeTaskStatus(taskId, 1)
    }
  });

  $(".button-done").on("click", function () {
    if (!($(this).closest(".done").length > 0)) {
      $(this).parents(".input-group").appendTo(".done");
      var taskId = $(this).parents(".input-group").attr("id").replace(/^\D+/g, '')
      changeTaskStatus(taskId, 2);
    }
  });

  $(".button-delete").on("click", function () {
    $(this).parents(".input-group").remove();
    var taskId = $(this).parents(".input-group").attr("id").replace(/^\D+/g, '')
    $.ajax({
      type: 'DELETE',
      dataType: 'json',
      contentType: "application/json",
      url: `http://127.0.0.1:5000/api/users/tasks/${taskId}`,
      headers: {
        "Authorization": `Bearer ${localStorage.getItem('access_token')}`
      },
      success: function () {
        // $(this).parents(".input-group").hide()
      }
    });
  });

  $(".button-share").on("click", function () {
    console.log('sharing arrow click')
    var taskId = $(this).parents(".input-group").attr("id").replace(/^\D+/g, '')
    $(".modal-dialog").attr("id", taskId);
    $("#sharingUsers ul").empty()
    loadSharingUsers();
    $("#sharingWindow").modal("show");
  });
}





$("input").keypress(function (e) {
  if (e.which == 13) {
    $("#add-button").click();
  }
});


function createTask(taskData) {
  shared_by_field = ''
  if (taskData.shared_by_name)
    shared_by_field = `Shared by: ${taskData.shared_by_name}`
  var internalElements = $(`
  <div class="input-group overflow" id="taskId${taskData.id}">
    <span class="taskTitle">${taskData.title}</span>
    <a
      data-toggle="collapse"
      href="#${taskData.id}"
      role="button"
      aria-expanded="false"
      aria-controls="${taskData.id}"
      style="font-size:14px; float: right;"
      
    >
      show more...
    </a>
    <div class="collapse" id="${taskData.id}">
      <div class="card card-body border-0">
        <div>
          ${taskData.description}
        </div>
        <div>
          ${shared_by_field}
        </div>
      </div>
    </div>
    <div class="button-container">
        <span class="button button-backlog">Backlog</span
        ><span class="button button-progress">In Progress</span
        ><span class="button button-done">Done</span
        ><span class="button button-delete">Delete</span>
        <span class="button-share" ><i class="fa-solid fa-share"></i></span>
    </div>
  </div>`);

  if (taskData.status == 0)
    $(".backlog").append(internalElements);
  else if (taskData.status == 1)
    $(".in-progress").append(internalElements);
  if (taskData.status == 2)
    $(".done").append(internalElements);
}


function createUserItem(user) {
  return `<li id="user_${user.id}" class="list-group-item border-right-0 border-left-0">
  <input
    class="form-check-input me-1"
    type="checkbox"
    value="${user.id}"
    aria-label="..."
  />
  ${user.username}
</li>`
}


function loadSharingUsers() {
  console.log('loading users');
  $.ajax({
    type: 'GET',
    dataType: 'json',
    contentType: "application/json",
    url: 'http://127.0.0.1:5000/api/users/sharing_users',
    headers: {
      "Authorization": `Bearer ${localStorage.getItem('access_token')}`
    },
    success: function (users) {

      users.forEach(function (user) {
        userListItem = createUserItem(user)
        $("#sharingUsers ul").append(userListItem);
      });
    }
  });
}


function loadData(data) {
  data.forEach(function (item) {
    // console.log(item);
    createTask(item)
  });
  addButtonActions();
}

$("#shareButton").on("click", (e) => {
  access_token = localStorage.getItem("access_token")
  taskId = $(".modal-dialog").attr("id")
  console.log(taskId)
  $('input:checked').each(function () {
    console.log(this.value);

    $.ajax({
      type: 'POST',
      dataType: 'json',
      contentType: "application/json",
      data: JSON.stringify({ "to_user": this.value }),
      url: `http://127.0.0.1:5000/api/users/tasks/${taskId}`,
      headers: {
        "Authorization": `Bearer ${access_token}`
      },
      success: function (data) {
      },
      error: function (xhr, ajaxOptions, thrownError) {
      }
    });
  });
})

$(document).ready(() => {

  token = localStorage.getItem('access_token');
  if (token !== null) {
    $("#navbarId").after(`<div>
                            <div class="flexColumn">
                              <div class="form">
                                <div class="flexColumn">
                                  <div class="flexRow">
                                    <input type="text" placeholder="Task..." id="inputTaskTitle" />
                                    <span id="add-button">Add</span>
                                  </div>
                                  <div class="flexRow">
                                   <textarea placeholder="Description..." id="inputTaskDescription"></textarea>
                                  </div>
                                  
                                </div>
                              </div>
                              <div class="flexRow">
                                <div class="scrum-board backlog">
                                  <h2>Backlog</h2>
                                </div>
                                <div class="scrum-board in-progress">
                                  <h2>In progress</h2>
                                </div>
                                <div class="scrum-board done">
                                  <h2>Done</h2>
                                </div>
                              </div>
                            </div>
                          </div>`);
    $("#add-button").on("click", function () {
      var taskTitle = $(this).prev().val();
      var taskDescription = $(this).prev().val();

      if (taskTitle === "" || taskDescription === "") {
        $(this).prev().val("");
        return alert("Input is empty!");
      }

      console.log(taskTitle, taskDescription)

      $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        url: `http://127.0.0.1:5000/api/users/tasks/create`,
        data: JSON.stringify({ "title": taskTitle, "description": taskDescription }),
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('access_token')}`
        },
        success: function (taskData) {
          createTask(taskData);
          addButtonActions();
        }
      });
    });
  } else {
    $("#navbarId").after(`
                        <h1 style="display: flex; justify-content: center; margin-top: 100px">
                        Please sign in
                        </h1>
                        `)
  }
  $.ajax({
    type: 'GET',
    dataType: 'json',
    contentType: "application/json",
    url: 'http://127.0.0.1:5000/api/users/tasks',
    headers: {
      "Authorization": `Bearer ${token}`
    },
    success: function (data) {
      // console.log('data: ', data);
      loadData(data);
    }
  });

});


