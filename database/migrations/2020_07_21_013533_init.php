<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class Init extends Migration {
    public function up() {
        Schema::create('sessions', function (Blueprint $table) {
            $table->char('id', 13);
            $table->float('total_virt_mem')->comment('MiB');
            $table->float('total_gpu_mem')->nullable()->comment('MiB');
            $table->float('total_disk_space')->comment('MiB');
            $table->text('gpu_name')->nullable();
            $table->char('token', 16);
            $table->primary('id');
        });
        Schema::create('logs', function (Blueprint $table) {
            $table->char('id', 13);
            $table->timestamp('time')->useCurrent();
            $table->float('5m_loadavg');
            $table->text('cpus_load')->comment("Range from 0 to 100");
            $table->float('virt_mem')->comment("Range from 0 to 1");
            $table->float('disk_usage')->comment("Range from 0 to 1");;
            $table->float('net_sent')->comment('MiB');
            $table->float('net_recv')->comment('MiB');
            $table->float('gpu_load')->nullable()->comment("Range from 0 to 1");
            $table->float('gpu_mem')->nullable()->comment("Range from 0 to 1");;
            $table->foreign('id')->references('id')->on('sessions');
            $table->unique(['id', 'time']);
        });
    }

    public function down() {
        Schema::drop('logs');
        Schema::drop('sessions');
    }
}
