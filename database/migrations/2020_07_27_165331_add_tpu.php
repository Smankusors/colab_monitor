<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class AddTpu extends Migration {
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up() {
        Schema::table('sessions', function (Blueprint $table) {
            $table->text('tpu_type')->nullable();
            $table->timestamp('created_at')->useCurrent();
        });
        Schema::table('logs', function (Blueprint $table) {
            $table->float('tpu_idle')->comment('Range from 0 to 100')->nullable();
            $table->float('tpu_mxu')->comment('Range from 0 to 100')->nullable();
        });
    }

    public function down() {
        Schema::table('sessions', function (Blueprint $table) {
            $table->dropColumn(['tpu_type', 'created_at']);
        });
        Schema::table('logs', function (Blueprint $table) {
            $table->dropColumn(['tpu_idle', 'tpu_mxu']);
        });
    }
}
