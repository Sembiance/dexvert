#!/usr/bin/env node
/* eslint-disable */
// AI VIBE CODED by Gemini 3 Flash Preview
const fs = require('fs');

if (process.argv.length < 4) {
    console.log("Usage: node mmf2vgm.js <input.json> <output.vgm>");
    process.exit(1);
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const smafData = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

// 44100 Hz / 250 ticks per sec = 176.4 samples per tick
const SAMPLES_PER_TICK = 176.4; 

const trackChunks = smafData.sub_chunks.filter(c => c.chunk_header?.signature.startsWith("MTR"));
const vgmEvents = [];
const patches = {};

// 1. Extract FM Voice Data
smafData.sub_chunks.forEach(chunk => {
    if (!chunk.sub_chunks) return;
    chunk.sub_chunks.forEach(sub => {
        if (!sub.exclusives) return;
        sub.exclusives.forEach(ex => {
            const v = ex.vm35_voice_pc || ex.vma_voice_pc;
            if (v && v.voice && v.voice.operators) patches[v.pc] = v.voice; 
        });
    });
});

// 2. Map Events to a timeline
trackChunks.forEach((mtrChunk, trIdx) => {
    const mtsq = mtrChunk.sub_chunks.find(s => s.chunk_header?.signature.startsWith("Mtsq"));
    if (!mtsq || !mtsq.events) return;

    let absoluteTick = 0;
    mtsq.events.forEach((item) => {
        absoluteTick += (item.duration || 0);
        const event = item.event;
        if (!event) return;

        // Spread tracks across the 6 Genesis channels
        const vgmIdx = (trIdx + (event.channel || 0)) % 6; 

        if (event.pc !== undefined) {
            vgmEvents.push({ type: 'patch', tick: absoluteTick, pc: event.pc, vgmIdx });
        }
        if (event.note !== undefined) {
            vgmEvents.push({ type: 'noteon', tick: absoluteTick, note: event.note, vgmIdx });
            vgmEvents.push({ type: 'noteoff', tick: absoluteTick + event.gate_time, vgmIdx });
        }
    });
});

vgmEvents.sort((a, b) => a.tick - b.tick);

// 3. Generate VGM binary stream
const vgmData = [];
const fnumTable = [617, 654, 693, 734, 778, 824, 873, 925, 980, 1038, 1100, 1165];
let lastSample = 0;

// State tracking to prevent "fluttering"
const currentPatchOnSlot = new Array(6).fill(-1);

vgmEvents.forEach(e => {
    let currentSample = Math.round(e.tick * SAMPLES_PER_TICK);
    let diff = currentSample - lastSample;
    while (diff > 0) {
        let wait = Math.min(diff, 0xFFFF);
        vgmData.push(0x61, wait & 0xFF, (wait >> 8) & 0xFF);
        diff -= wait;
    }

    const slot = e.vgmIdx; 
    const port = slot < 3 ? 0x52 : 0x53;
    const baseReg = slot % 3;

    if (e.type === 'patch' && patches[e.pc]) {
        // FLUTTER FIX: Only write registers if the patch has actually changed on this slot
        if (currentPatchOnSlot[slot] === e.pc) return;
        currentPatchOnSlot[slot] = e.pc;

        const p = patches[e.pc];
        vgmData.push(port, 0xB4 + baseReg, 0xC0); // Stereo
        vgmData.push(port, 0xB0 + baseReg, (p.fb << 3) | (p.alg & 0x07));
        
        p.operators.forEach((op, i) => {
            const opOff = [0, 8, 4, 12][i] + baseReg; 
            vgmData.push(port, 0x30 + opOff, (op.mult || 0) & 0x0F);
            // Volume logic: SMAF TL is 0-63, Genesis is 0-127. 
            // We scale and add floor (32) to prevent the "buzz" distortion.
            const tl = Math.min(127, (op.tl * 1.5) + 24);
            vgmData.push(port, 0x40 + opOff, tl | 0); 
            vgmData.push(port, 0x50 + opOff, (op.ar << 4) | 0x05); // Balanced Attack
            vgmData.push(port, 0x60 + opOff, (op.dr << 4) | 0x02); // Balanced Decay
            vgmData.push(port, 0x80 + opOff, (op.sl << 4) | (op.rr & 0x0F));
        });
    } else if (e.type === 'noteon') {
        const block = Math.floor(e.note / 12) - 1;
        const fnum = fnumTable[e.note % 12];
        vgmData.push(port, 0xA4 + baseReg, ((block & 0x07) << 3) | (fnum >> 8));
        vgmData.push(port, 0xA0 + baseReg, fnum & 0xFF);
        const vgmChan = slot < 3 ? slot : slot + 1; 
        vgmData.push(0x52, 0x28, 0xF0 | vgmChan); 
    } else if (e.type === 'noteoff') {
        const vgmChan = slot < 3 ? slot : slot + 1;
        vgmData.push(0x52, 0x28, 0x00 | vgmChan);
    }
    lastSample = currentSample;
});

vgmData.push(0x66);
const header = Buffer.alloc(0x80);
header.write("Vgm ", 0x00);
header.writeUInt32LE(vgmData.length + 0x80 - 4, 0x04);
header.writeUInt32LE(0x150, 0x08);
header.writeUInt32LE(7670454, 0x2C);
header.writeUInt32LE(lastSample, 0x18);
header.writeUInt32LE(0x80 - 0x34, 0x34); 

fs.writeFileSync(outputPath, Buffer.concat([header, Buffer.from(vgmData)]));
console.log(`VGM generated: ${outputPath}`);