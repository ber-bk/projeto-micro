(function ()
{
  'use strict';
  angular.module('ProjetoMicroApp', [])
  .controller('ProjetoMicroController', Controller);
  Controller.$inject = ['$scope', '$filter'];

  function Controller($scope, $filter)
  {
    $scope.CriarMissao      = false;
    $scope.SelecionarMissao = false;
    $scope.ExibirMissao     = false;





  };

}
)
();