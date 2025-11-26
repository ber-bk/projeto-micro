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

    $scope.AlterarViewCriarMissao = function ()
    {
      $scope.CriarMissao      = true;
      $scope.SelecionarMissao = false;
      $scope.ExibirMissao     = false;
    };

    $scope.AlterarViewSelecionarMissao = function ()
    {
      $scope.CriarMissao      = false;
      $scope.SelecionarMissao = true;
      $scope.ExibirMissao     = false;
    };

    $scope.AlterarViewExibirMissao = function ()
    {
      $scope.CriarMissao      = false;
      $scope.SelecionarMissao = false;
      $scope.ExibirMissao     = true;
    };




  };

}
)
();