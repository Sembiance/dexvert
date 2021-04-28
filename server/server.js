#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	C = require("../lib/C.js"),
	fastify = require("fastify")({logger : {level : "warn"}});

let stopping = false;
const subServers = ["unoconv", "ftp", "qemu"].map(v => require(`./${v}.js`));	// eslint-disable-line node/global-require

function stop()
{
	if(stopping)
		return;
		
	XU.log`Stopping dexserv...`;
	stopping = true;

	subServers.parallelForEach((subServer, subcb) => subServer.stop(subcb), XU.FINISH);
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
		
		fastify.get("/status", (request, reply) => reply.send({status : (subServers.every(subServer => subServer.status()) ? C.DEXSERV_OK_RESPONSE : "error: one or more sub-servers are not running correctly")}));
		subServers.forEach(subServer =>
		{
			if(subServer.registerRoutes)
				subServer.registerRoutes(fastify);
		});

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
		subServers.parallelForEach((subServer, subcb) => subServer.start(subcb), this);
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

