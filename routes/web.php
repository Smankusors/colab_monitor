<?php /** @var Laravel\Lumen\Routing\Router $router */
$router->get('/', function () use ($router) {
    return $router->app->version();
});

$router->post('/', ['uses' => 'Controller@NewSession']);
$router->get('/{id}', ['uses' => 'Controller@ViewSession']);
$router->post('/{id}', ['uses' => 'Controller@UpdateSession']);
