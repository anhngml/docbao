

var docbao =  angular.module('docbaoApp', []);

docbao.controller('logCtrl', function($scope, $http)
{
    $http.get('log_data.json').then(function (response)
    {
        $scope.log = response.data; //success callback
    }
    , function (data){
        console.log("Khong doc duoc file log_data.json");
    }    //fail callback
    );

   $http.get('article_data.json').then(function (response)
    {
        $scope.articles = response.data.article_list; //success callback
        draw_article_table(response.data.article_list);
        
        setup_auto_complete(response.data.article_list);
    }
    , function (data){
        console.log("Khong doc duoc file article_data.json");
    }    //fail callback
    );

   $http.get('keyword_dict.json').then(function (response)
    {
        draw_category_table(response.data.data);
    }
    , function (data){
        console.log("Khong doc duoc file keyword_dict.json");
    }    //fail callback
    );

   $http.get('hot_keyword.json').then(function (response)
    {
        var data = response.data;
        draw_hot_keyword_barchart(data);
        
        var keyword_list = Object.keys(data);
        var keyword_string = "";
        for(var i=0; i<keyword_list.length; i++)
            {
                keyword_string = keyword_string + keyword_list[i] + " - ";
            }
        console.log(keyword_string);
        $scope.keyword_string = keyword_string;

        
    }
    , function (data){
        console.log("Khong doc duoc file hot_keyword.json");
    }    //fail callback
    );
});

function draw_hot_keyword_barchart(hot_keyword_dict)
{
    // -- Bar Chart Example
console.log(hot_keyword_dict);
var ctx = document.getElementById("myBarChart");
var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: Object.keys(hot_keyword_dict),
    datasets: [{
      label: "số bài báo chứa từ khóa này",
      backgroundColor: "rgba(2,117,216,1)",
      borderColor: "rgba(2,117,216,1)",
      data: Object.values(hot_keyword_dict),
    }],
  },
  options: {
    onClick: function(evt){
    var activeElement = myLineChart.getElementAtEvent(evt)[0]._index;
    var search_string = Object.keys(hot_keyword_dict)[activeElement];
    if(confirm("Đọc các bài báo có chứa từ khóa: " + search_string))
    {
        table = $('#article_table').DataTable();
        table.search(search_string).draw();
        var new_position = $("#article_table").offset();
        //window.scrollTo(new_position.left,new_position.top);

        $('html, body').animate({
          scrollTop: $("#article_table").offset().top
        }, 900);
    }
    }
  }
    });
}

function draw_article_table(article_list)
{
var dataset = article_list;
 
$(document).ready(function() {
    $('#article_table').DataTable( {
        data: dataset,
        columns: [
            { title: "STT", data:"stt", "searchable": false, className: "min-desktop"},
            { title: "Tên bài", data:"topic", "searchable": true, className:"all"},
            { title: "Nguồn báo", data:"newspaper", "searchable": false, className:"min-desktop"},
            { title: "Cập nhật", data:"update_time", "searchable": false, className: "min-desktop" },
            { title: "Ngày xuất bản", data:"publish_time", "searchable": false, className: "min-desktop" },
        ],
        "rowCallback": function( row, data, index ) {
            topic = $('td:eq(1)', row).html();
            $('td:eq(1)', row).html('<a href="' + data.href + '" target="_blank">' + topic + '</a>');
          },
        responsive: true,
        columnDefs: [
            { responsivePriority: 1, targets: 1 },
            { responsivePriority: 2, targets: 2 }
        ],
        nowrap: true
    } );
    } );
}


function draw_category_table(category_list)
{
var dataset = category_list;
console.log(dataset);
$(document).ready(function() 
    {
        $('#category_table').DataTable( {
            data: dataset,
            columns: [
                { title: "Chuyên mục", data:"category"},
                { title: "Keyword", data:"keywords"},

            ],
            "ordering": false,
            "autoWidth": false,
            "rowCallback": function( row, data, index ) {
                topic = $('td:eq(1)', row).html();
                keyword_string = "";
                console.log(data);
                for(i=0; i< data.keywords.length; i++)
                {
                    keyword_string = keyword_string + '<a href="#article_table" onclick ="search_article_table(this)">' + 
                    data.keywords[i].keyword + '</a>' + '<sub>(' + data.keywords[i].count +
                     ')</sub>' + ' - ';
                }

                $('td:eq(1)', row).html(keyword_string);
              }
        } );
    } );
}

function _search_article_table(search_string)
{
    if(confirm("Đọc các bài báo có chứa từ khóa: " + search_string))
        {
        table = $('#article_table').DataTable();
        table.search(search_string).draw();

        $('html, body').animate({
          scrollTop: $("#article_table").offset().top
        }, 900);
    }
}

function search_article_table(keyword)
{
    search_string = keyword.text;
    _search_article_table(search_string);
}

function keyup_on_keyword_search_text(event)
{
    if (event.keyCode === 13) {
        search_keyword();
    }
}

function search_keyword()
{
    _search_article_table($("#keyword_search_text").val());
}

function go_to_search_card()
{
    $('html, body').animate({
      scrollTop: $("#search_card").offset().top
    }, 900);
}

function setup_auto_complete(article_list)
{
    var states = []
    for(var i=0; i<article_list.length; i++)
    {
        states.push({"title":article_list[i].topic + " (" + article_list[i].newspaper + ")", "value": article_list[i].topic});
    }
  $("#keyword_search_text").autocomplete({
    source:[states]
    
    });
}