#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	C = require("../lib/C.js"),
	unoconv = require("./unoconv.js"),
	qemu = require("./qemu.js"),
	fastify = require("fastify")({logger : {level : "warn"}});

let stopping = false;

function stop()
{
	if(stopping)
		return;
		
	XU.log`Stopping dexserv...`;
	stopping = true;

	tiptoe(
		function stopSubServers()
		{
			unoconv.stop(this.parallel());
			qemu.stop(this.parallel());
		},
		function wait()
		{
			setTimeout(this, XU.SECOND*2);
		},
		XU.FINISH
	);
}

process.on("SIGTERM", () =>
{
	XU.log`${XU.c.blink + XU.cf.fg.red("***")} Terminate caught.`;
	stop();
});

process.on("SIGINT", () =>
{
	XU.log`${XU.c.blink + XU.cf.fg.red("***")} Interrupt caught.`;
	stop();
});

process.on("uncaughtException", err =>
{
	XU.log`${XU.c.blink + XU.cf.fg.red("***")} Uncaught exception.`;
	console.error(err);
	stop();
});

tiptoe(
	function registerRoutes()
	{
		XU.log`Registering routes...`;
		fastify.get("/status", (request, reply) => reply.send({status : (unoconv.status() && qemu.status() ? C.DEXSERV_OK_RESPONSE : "error: one or more sub-servers are not running correctly")}));
		qemu.registerRoutes(fastify);

		fastify.ready(this);
	},
	function startServer()
	{
		XU.log`Routes registered:`;
		console.log(fastify.printRoutes());

		fastify.listen({port : C.DEXSERV_PORT, host : C.DEXSERV_HOST}, this);
	},
	function startSubServers()
	{
		XU.log`Starting sub-servers...`;
		unoconv.start(this.parallel());
		qemu.start(this.parallel());
	},
	function finish(err)
	{
		if(err)
		{
			console.error(err);
			process.exit(1);
		}
	}
);

