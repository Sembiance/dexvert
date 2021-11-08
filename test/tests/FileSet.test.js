import {assertStrictEquals, assertThrowsAsync, assertEquals} from "https://deno.land/std@0.111.0/testing/asserts.ts";
import {FileSet} from "../../src/FileSet.js";
import {DexFile} from "../../src/DexFile.js";
import {fileUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import {encode as base64Encode} from "https://deno.land/std@0.113.0/encoding/base64.ts";

Deno.test("create", async () =>
{
	const a = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	const b = await FileSet.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", files : {main : ["some.big.txt.file.txt", "subDir/txt.b", "subDir/symlinkFile", "subDir/more_sub/c.txt", "subDir/more_sub/third"]}});
	const c = b.clone();
	const d = b.clone();
	const e = await FileSet.create({main : [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]});
	d.changeRoot("/tmp/path/dir");

	[a, b, c, e].forEach(o =>
	{
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.files.main.length, 5);
		assertStrictEquals(o.all.length, 5);
		assertStrictEquals(o.main.name, "some.big.txt.file");
		assertStrictEquals(o.main.size, 6);
		assertStrictEquals(o.all[2].isSymlink, true);
		assertStrictEquals(o.files.main[2].isSymlink, true);
	});
});

Deno.test("changeRoot", async () =>
{
	const a = await FileSet.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", files : {main : ["some.big.txt.file.txt", "subDir/txt.b", "subDir/symlinkFile", "subDir/more_sub/c.txt", "subDir/more_sub/third"]}});
	const b = a.clone();
	b.changeRoot("/some/other/dir/");

	// test original
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.files.main.length, 5);
	assertStrictEquals(a.all.length, 5);
	assertStrictEquals(a.main.name, "some.big.txt.file");
	assertStrictEquals(a.main.size, 6);
	assertStrictEquals(a.all[2].isSymlink, true);
	assertStrictEquals(a.files.main[2].isSymlink, true);
	assertStrictEquals(a.all[2].rel, "subDir/symlinkFile");

	// test clone
	assertStrictEquals(b.root, "/some/other/dir");
	assertStrictEquals(b.files.main.length, 5);
	assertStrictEquals(b.all.length, 5);
	assertStrictEquals(b.main.name, "some.big.txt.file");
	assertStrictEquals(b.main.size, 6);
	assertStrictEquals(b.all[2].isSymlink, true);
	assertStrictEquals(b.files.main[2].isSymlink, true);
	assertStrictEquals(b.all[2].rel, "subDir/symlinkFile");
	assertStrictEquals(b.all[2].root, "/some/other/dir");
	assertStrictEquals(b.all[2].absolute, "/some/other/dir/subDir/symlinkFile");
	assertStrictEquals(b.all[2].dir, "/some/other/dir/subDir");
	assertStrictEquals(b.all[2].name, "symlinkFile");
});

Deno.test("addFile", async () =>
{
	const a = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"]);
	await a.add("/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile");
	await a.add("main", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt");
	await a.add("main", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third");
	const b = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"]);
	await b.addAll("main", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);

	[a, b].forEach(o =>
	{
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.files.main.length, 5);
		assertStrictEquals(o.all.length, 5);
		assertStrictEquals(o.main.name, "some.big.txt.file");
		assertStrictEquals(o.main.size, 6);
		assertStrictEquals(o.files.main[2].isSymlink, true);
		assertStrictEquals(o.all[2].isSymlink, true);
		assertStrictEquals(o.files.main[2].isSymlink, true);
	});

	assertThrowsAsync(async () => await a.add(await DexFile.create("/mnt/compendium/DevLab/dexvert/.gitignore")));
});

Deno.test("rsyncTo", async () =>
{
	const a = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);

	const tmpDirPath = await fileUtil.genTempPath();
	await Deno.mkdir(tmpDirPath);
	await a.rsyncTo(tmpDirPath);
	assertEquals(await fileUtil.tree(tmpDirPath), [
		"subDir",
		"subDir/symlinkFile",
		"subDir/more_sub",
		"subDir/more_sub/c.txt",
		"subDir/more_sub/third",
		"subDir/txt.b",
		"some.big.txt.file.txt"].map(v => path.join(tmpDirPath, v)));
	await Deno.remove(tmpDirPath, {recursive : true});
	await Deno.mkdir(tmpDirPath);
	await a.rsyncTo(tmpDirPath, {type : "other"});
	assertEquals(await fileUtil.tree(tmpDirPath), [
		"subDir",
		"subDir/more_sub",
		"subDir/more_sub/c.txt",
		"subDir/symlinkFile"].map(v => path.join(tmpDirPath, v)));
});

Deno.test("pretty", async () =>
{
	const a = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);

	assertStrictEquals(base64Encode(a.pretty()), "G1s5N21GaWxlU2V0G1swbSAbWzk2bSgbWzBtG1s5N21yb290IBtbMG0bWzM1bS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtKRtbMG0gaGFzIBtbOTdtNRtbMG0gZmlsZXM6CgkbWzM4OzU7MjUwbUYbWzBtIBtbOTdtICAgIDZiG1swbSAbWzkzbS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtLxtbMG0bWzMzbXNvbWUuYmlnLnR4dC5maWxlLnR4dBtbMG0KCRtbMzg7NTsyNTBtRhtbMG0gG1s5N20gICAgOGIbWzBtIBtbOTNtL21udC9jb21wZW5kaXVtL0RldkxhYi9kZXh2ZXJ0L3Rlc3QvZmlsZXMbWzBtG1s5Nm0vG1swbRtbMzNtc3ViRGlyL3R4dC5iG1swbQoJG1s5NW1EG1swbSAbWzk3bSAgIDRLQhtbMG0gG1s5M20vbW50L2NvbXBlbmRpdW0vRGV2TGFiL2RleHZlcnQvdGVzdC9maWxlcxtbMG0bWzk2bS8bWzBtG1szM21zdWJEaXIvbW9yZV9zdWIvdGhpcmQbWzBtCgkbWzk2bUwbWzBtIBtbOTdtICAgMTRiG1swbSAbWzkzbS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtLxtbMG0bWzMzbXN1YkRpci9zeW1saW5rRmlsZRtbMG0KCRtbMzg7NTsyNTBtRhtbMG0gG1s5N20gICAxMGIbWzBtIBtbOTNtL21udC9jb21wZW5kaXVtL0RldkxhYi9kZXh2ZXJ0L3Rlc3QvZmlsZXMbWzBtG1s5Nm0vG1swbRtbMzNtc3ViRGlyL21vcmVfc3ViL2MudHh0G1swbQ==");	// eslint-disable-line max-len
});

const fileSetJSON = `{"root":"/mnt/compendium/DevLab/dexvert/test/files","files":{"main":[{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"some.big.txt.file.txt","absolute":"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt","base":"some.big.txt.file.txt","dir":"/mnt/compendium/DevLab/dexvert/test/files","name":"some.big.txt.file","ext":".txt","preExt":".some","preName":"big.txt.file.txt","isFile":true,"isDirectory":false,"isSymlink":false,"size":6,"ts":1635685469027},{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/txt.b","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b","base":"txt.b","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir","name":"txt","ext":".b","preExt":".txt","preName":"b","isFile":true,"isDirectory":false,"isSymlink":false,"size":8,"ts":1635685484995},{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/more_sub/third","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third","base":"third","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub","name":"third","ext":"","preExt":"","preName":"third","isFile":false,"isDirectory":true,"isSymlink":false,"size":4096,"ts":1635685489475}],"other":[{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/symlinkFile","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile","base":"symlinkFile","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir","name":"symlinkFile","ext":"","preExt":"","preName":"symlinkFile","isFile":false,"isDirectory":false,"isSymlink":true,"size":14,"ts":1635685795866},{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"subDir/more_sub/c.txt","absolute":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt","base":"c.txt","dir":"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub","name":"c","ext":".txt","preExt":".c","preName":"txt","isFile":true,"isDirectory":false,"isSymlink":false,"size":10,"ts":1635685592959}]}}`; // eslint-disable-line max-len
Deno.test("serialize", async () =>
{
	const a = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	await a.addAll("other", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt"]);

	assertStrictEquals(JSON.stringify(a.serialize()), fileSetJSON);
});

Deno.test("deserialize", () =>
{
	const a = FileSet.deserialize(JSON.parse(fileSetJSON));	// eslint-disable-line no-restricted-syntax
	assertStrictEquals(base64Encode(a.pretty()), "G1s5N21GaWxlU2V0G1swbSAbWzk2bSgbWzBtG1s5N21yb290IBtbMG0bWzM1bS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtKRtbMG0gaGFzIBtbOTdtNRtbMG0gZmlsZXM6CgkbWzM4OzU7MjUwbUYbWzBtIBtbOTdtICAgIDZiG1swbSAbWzkzbS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtLxtbMG0bWzMzbXNvbWUuYmlnLnR4dC5maWxlLnR4dBtbMG0KCRtbMzg7NTsyNTBtRhtbMG0gG1s5N20gICAgOGIbWzBtIBtbOTNtL21udC9jb21wZW5kaXVtL0RldkxhYi9kZXh2ZXJ0L3Rlc3QvZmlsZXMbWzBtG1s5Nm0vG1swbRtbMzNtc3ViRGlyL3R4dC5iG1swbQoJG1s5NW1EG1swbSAbWzk3bSAgIDRLQhtbMG0gG1s5M20vbW50L2NvbXBlbmRpdW0vRGV2TGFiL2RleHZlcnQvdGVzdC9maWxlcxtbMG0bWzk2bS8bWzBtG1szM21zdWJEaXIvbW9yZV9zdWIvdGhpcmQbWzBtCgkbWzk2bUwbWzBtIBtbOTdtICAgMTRiG1swbSAbWzkzbS9tbnQvY29tcGVuZGl1bS9EZXZMYWIvZGV4dmVydC90ZXN0L2ZpbGVzG1swbRtbOTZtLxtbMG0bWzMzbXN1YkRpci9zeW1saW5rRmlsZRtbMG0KCRtbMzg7NTsyNTBtRhtbMG0gG1s5N20gICAxMGIbWzBtIBtbOTNtL21udC9jb21wZW5kaXVtL0RldkxhYi9kZXh2ZXJ0L3Rlc3QvZmlsZXMbWzBtG1s5Nm0vG1swbRtbMzNtc3ViRGlyL21vcmVfc3ViL2MudHh0G1swbQ==");	// eslint-disable-line max-len
	assertStrictEquals(JSON.stringify(a.serialize()), fileSetJSON);
});
