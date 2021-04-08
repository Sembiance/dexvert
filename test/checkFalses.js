"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	testUtil = require("./testUtil.js"),
	dexUtil = require("../lib/dexUtil.js"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

const EXPECTED =
{
	archive :
	{
		adfOFS          : ["killingjoke.adf", "voyager.adf"],
		atr             : "rambrandt.atr",
		gemResourceFile : "daleks.rsc",
		msa             : "adr_1.msa"
	},
	audio :
	{
		siff : "test2.son"
	},
	executable :
	{
		gfaBASICAtari : true
	},
	font :
	{
		nlq : true
	},
	image :
	{
		cgm                   : "input.cgm",
		hdf4				  : ["input_truecolor.hdf", "input_256.hdf"],
		hip                   : "aga2.hps",
		hlr                   : "autumn edition, 7).hlr",
		jbig                  : "mx.jbg",
		koalaMicroillustrator : ["starwar.pic", "apollo.pic"],
		prismPaint            : "pat_16.tpi",
		sgx                   : "testimg-lz77.sgx",
		snx                   : true,
		spectrum512S          : ["ai_r_010.sps", "amber_f.sps", "candle.sps"]
	},
	text :
	{
		c : "source_hacking"
	}
};

const testDataFilePath = path.join(testUtil.DATA_DIR_PATH, "process.json");
const GARBAGE = "_neverGonnaGiveYouUpOrEndWithThisʘ";
const SEEN_EXPECTED = [];

tiptoe(
	function loadTestData()
	{
		fs.readFile(testDataFilePath, XU.UTF8, this.parallel());
		dexUtil.findFormats(this.parallel());
	},
	function checkFalses(testDataRaw, formatData)
	{
		Object.forEach(JSON.parse(testDataRaw), (filename, result) =>
		{
			if(result.processed)
				return;
			
			const [family, formatid] = filename.split("/");
			if(formatData[family][formatid].meta.unsupported)
				return;

			if(EXPECTED?.[family]?.[formatid]===true || Array.force(EXPECTED?.[family]?.[formatid] || GARBAGE).some(v => filename.toLowerCase().endsWith(v)))
			{
				SEEN_EXPECTED.pushUnique(`${family}/${formatid}`);
				return;
			}

			XU.log`UNEXPECTED! ${filename} was NOT processed!`;
		});

		const notSeen = Object.entries(EXPECTED).flatMap(([family, formats]) => Object.keys(formats).map(format => `${family}/${format}`)).subtractOnce(SEEN_EXPECTED);
		if(notSeen.length>0)
			XU.log`The following EXPECTED items were not seen as unprocessed: ${notSeen}`;

		this();
	},
	XU.FINISH
);
