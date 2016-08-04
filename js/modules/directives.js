app.directive('histogram', function ($timeout, $window) {
    return {
        restrict: 'EA',
        scope: {
            title: '@title',
            width: '@width',
            height: '@height',
            bins: '@bins',
            zoomin: '@zoomin',
            viewmax: '@viewmax',
            simdata: '=simdata',
            redraw: '@redraw',
            data: '=data'
        },
        link: function ($scope, $elm, $attr) {
            $scope.width = $window.innerWidth*0.9;
            angular.element($window).bind('resize', function(){
                $scope.width = $window.innerWidth*0.9;
                draw();
                $scope.$digest();
            });

            // Create the data table and instantiate the chart
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Trial');
            data.addColumn('number', 'Amplitude');
            data.addColumn('number', 'Simulated Amplitude');
            var chart = new google.visualization.Histogram($elm[0]);

            draw();

            // Watches, to refresh the chart when its data, title or dimensions change
            $scope.$watch('data', function () {
                draw();
            }, true); // true is for deep object equality checking
            $scope.$watch('simdata', function () {
                draw();
            }, true);
            $scope.$watch('title', function () {
                draw();
            });
            $scope.$watch('bins', function () {
                draw();
            });
            $scope.$watch('viewmax', function () {
                draw();
            });
            $scope.$watch('zoomin', function () {
                draw();
            });
            $scope.$watch('redraw', function () {
                draw();
            });

            function draw() {
                if ($scope.data == undefined) return;
                if (!draw.triggered) {
                    draw.triggered = true;
                    $timeout(function () {
                        draw.triggered = false;
                        var label, value;
                        data.removeRows(0, data.getNumberOfRows());
                        for (var i = 0; i < $scope.data.length; i++) {
                            var row;
                            if ($scope.simdata == undefined) {
                                row = $scope.data[i].slice();
                                row[2] = undefined;
                            } else {
                                row = $scope.data[i].slice();
                                row[2] = $scope.simdata[i];
                            }
                            data.addRow(row);
                        }
                        var options = {
                            'title': $scope.title,
                            'width': $scope.width,
                            'height': $scope.width*5/8,
                            'histogram': {'bucketSize': $scope.bins},
                            'dataOpacity': 0.8
                        };
                        if ($scope.zoomin == 'set') {
                            options.vAxis = {};
                            options.vAxis.viewWindow = {};
                            options.vAxis.viewWindow.max = $scope.viewmax;
                        }
                        google.visualization.events.addListener(chart, 'ready', function () {
                          document.getElementById('download').innerHTML =
                            '<a class="btn btn-default" target="_blank" href="' + chart.getImageURI() + '">Download Histogram</a>';
                        });
                        chart.draw(data, options);

                    }, 0, true);
                }
            }
        }
    };
});
