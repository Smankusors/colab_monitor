<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class Init extends Migration {
    public function up() {
        Schema::create('sessions', function (Blueprint $table) {
            $table->char('id', 13);
            $table->integer('total_virt_mem');
            $table->integer('total_gpu_mem');
            $table->integer('total_disk_space');
            $table->text('gpu_name');
            $table->primary('id');
        });
        Schema::create('logs', function (Blueprint $table) {
            $table->char('id', 13);
            $table->timestamp('time')->useCurrent();
            $table->float('5m_loadavg');
            $table->text('cpus_load');
            $table->float('virt_mem');
            $table->float('disk_usage');
            $table->integer('net_bytes_sent');
            $table->integer('net_bytes_recv');
            $table->float('gpu_load');
            $table->float('gpu_mem');
            $table->foreign('id')->references('id')->on('sessions');
            $table->unique(['id', 'time']);
        });

    }

    public function down() {
        Schema::drop('logs');
        Schema::drop('sessions');
    }
}
