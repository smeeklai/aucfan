var djangoTodo = angular.module('djangoTodo', []);

function mainController($scope, $http) {

    // $scope.readTodos = function() {
    //     $http.get('/api/todos/')
    //         .success(function(data) {
    //             $scope.formData = {};
    //             $scope.todos = data;
    //             console.log(data);
    //         })
    //         .error(function(data) {
    //             console.log('Error: ' + data);
    //         });
    // };

    $scope.predict = function(jan) {
        $http.post('/api/predict/'+jan)
            .success(function(data) {
                console.log(data);
                $scope.todos = data;
            })
            .error(function(data) {
                console.log('Error: ' + data);
            });
    };


     //$scope.readTodos();

}