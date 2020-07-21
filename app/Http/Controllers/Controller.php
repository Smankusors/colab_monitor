<?php
namespace App\Http\Controllers;

use Illuminate\Database\QueryException;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\DB;
use Laravel\Lumen\Routing\Controller as BaseController;

class Controller extends BaseController {
    /**
     * Initialize new session based on the sent data,
     * and then returns the session id
     *
     * @param Request $request
     * @return Response
     */
    public function NewSession(Request $request) {
        while (True) {
            $id = uniqid();
            if (!DB::table('sessions')->where('id', $id)->exists())
                break;
        }
        $data = $request->all();
        $data['id'] = $id;
        try {
            DB::table('sessions')->insert($data);
        } catch (QueryException $e) {
            //if there's unknown column, i.e. someone sent bad data,
            if ($e->getCode() === "42S22")
                return new Response('', 400);
            if ($e->errorInfo[0] === 'HY000')
                //if some column required missing on the data
                if ($e->errorInfo[1] === 1364)
                    return new Response('', 400);
            throw $e;
        }

        return new Response($id);
    }

    /**
     * Update the given session $id
     *
     * @param Request $request
     * @param string $id session ID
     * @return Response
     */
    public function UpdateSession(Request $request, $id) {
        if (!DB::table('sessions')->where('id', $id)->exists())
            return new Response('', 404);
        $data = $request->all();
        $data['id'] = $id;
        $data['cpus_load'] = join(',', $data['cpus_load']);
        try {
            DB::table('logs')->insert($data);
        } catch (QueryException $e) {
            //if there's unknown column, i.e. someone sent bad data,
            if ($e->getCode() === "42S22")
                return new Response('', 400);
            if ($e->errorInfo[0] === 'HY000')
                //if some column required missing on the data
                if ($e->errorInfo[1] === 1364)
                    return new Response('', 400);
            throw $e;
        }

        return new Response();
    }

    public function ViewSession(Request $request, $id) {
        $sessionInfo = DB::table('sessions')->where('id', $id)->first();
        if ($sessionInfo === null)
            return new Response('', 404);
        $logs = DB::table('logs')->where('id', $id)->orderBy('time', 'desc')->get();
        return view('session_info', [
            'sessionInfo' => $sessionInfo,
            'logs' => $logs
        ]);
    }
}
