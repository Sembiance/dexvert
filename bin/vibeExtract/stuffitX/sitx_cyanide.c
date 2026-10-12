/* Vibe coded by Codex
 * Checked Cyanide decoder, adapted from XADMaster's
 * XADStuffItXCyanideHandle.m, CarrylessRangeCoder.m and BWT.c.
 * Copyright (c) 2017-present, MacPaw Way Ltd. All rights reserved.
 * LGPL-2.1-or-later; distributed WITHOUT ANY WARRANTY.
 * See LICENSE-XADMaster.txt.
 * Build: cc -O2 -std=c99 -fPIC -shared sitx_cyanide.c -o libsitx_cyanide.so
 */
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const uint8_t *data;
    size_t size, pos;
    int error;
} Input;

typedef struct {
    Input *input;
    uint32_t low, code, range;
} Coder;

typedef struct {
    unsigned count;
    uint32_t frequency[256], mapping[256];
} Model;

static uint8_t read_byte(Input *in)
{
    if (in->pos == in->size) {
        in->error = 1;
        return 0;
    }
    return in->data[in->pos++];
}

static uint32_t read_u32(Input *in)
{
    uint32_t value = 0;
    for (int i = 0; i < 4; i++) value = (value << 8) | read_byte(in);
    return value;
}

static void normalize(Coder *coder)
{
    while (!coder->input->error) {
        if ((coder->low ^ (coder->low + coder->range)) >= 0x1000000) {
            if (coder->range >= 0x10000) break;
            coder->range = (0u - coder->low) & 0xffff;
        }
        coder->code = (coder->code << 8) | read_byte(coder->input);
        coder->low <<= 8;
        coder->range <<= 8;
    }
}

static int next_symbol(Coder *coder, const uint32_t *freq, unsigned count)
{
    uint32_t total = 0, cumulative = 0;
    for (unsigned i = 0; i < count; i++) total += freq[i];
    if (!total || coder->input->error) return -1;
    coder->range /= total;
    if (!coder->range) return -1;
    uint32_t value = (coder->code - coder->low) / coder->range;
    if (value >= total) return -1;
    for (unsigned i = 0; i < count; i++) {
        if (value < cumulative + freq[i]) {
            coder->low += coder->range * cumulative;
            coder->range *= freq[i];
            normalize(coder);
            return coder->input->error ? -1 : (int)i;
        }
        cumulative += freq[i];
    }
    return -1;
}

static void init_model(Model *model, unsigned count)
{
    model->count = count;
    for (unsigned i = 0; i < count; i++) {
        model->frequency[i] = 1;
        model->mapping[i] = count - i - 1;
    }
}

static unsigned bump(Model *model, unsigned index, uint32_t maximum)
{
    uint32_t total = 0;
    for (unsigned i = 0; i < model->count; i++) total += model->frequency[i];
    if (total >= maximum) {
        for (unsigned i = 0; i < model->count; i++)
            model->frequency[i] = (model->frequency[i] + 1) / 2;
    }
    unsigned last = index;
    while (last + 1 < model->count &&
            model->frequency[last + 1] == model->frequency[index]) last++;
    uint32_t temp = model->mapping[index];
    model->mapping[index] = model->mapping[last];
    model->mapping[last] = temp;
    model->frequency[last]++;
    return last;
}

static void ternary_order(const uint32_t *freq, unsigned *order)
{
    uint32_t a = freq[0], b = freq[1], c = freq[2];
    if (a < b) {
        if (a < c) {
            order[0] = 0;
            order[1] = b < c ? 1 : 2;
            order[2] = b < c ? 2 : 1;
        } else { order[0] = 2; order[1] = 0; order[2] = 1; }
    } else if (b < c) {
        order[0] = 1;
        order[1] = c < a ? 2 : 0;
        order[2] = c < a ? 0 : 2;
    } else { order[0] = 2; order[1] = 1; order[2] = 0; }
}

static int decode_block(Input *in, uint8_t *block, uint32_t size, unsigned symbols)
{
    static const unsigned groups[27] = {
        0,1,2,3,4,5,6,7,8,3,9,10,3,4,5,11,11,8,6,2,5,6,7,8,12,12,13
    };
    Coder coder = {in, 0, 0, UINT32_MAX};
    coder.code = read_u32(in);
    uint32_t markov[14][3] = {{0}};
    Model low[8], high;
    unsigned shift = 1;
    while (symbols) {
        unsigned count = 1u << shift;
        if (symbols < (3u << shift)) count = symbols;
        init_model(&low[shift - 1], count);
        symbols -= count;
        shift++;
    }
    init_model(&high, shift);

    unsigned prev = 0, prev2 = 0, prev3 = 0;
    int zero_run = 1;
    for (uint32_t i = 0; i < size; i++) {
        unsigned context = groups[prev3 * 9 + prev2 * 3 + prev];
        uint32_t *freq = markov[context], sorted[3];
        unsigned order[3];
        ternary_order(freq, order);
        for (int j = 0; j < 3; j++) sorted[j] = freq[order[j]] + 1;
        int symbol = next_symbol(&coder, sorted, 3);
        if (symbol < 0) return -1;
        unsigned ternary = order[symbol];
        if (!ternary && !zero_run && !context) {
            zero_run = 1;
            for (int j = 0; j < 3; j++) freq[j] >>= 1;
            freq[0] += 3;
            block[i] = 0;
        } else {
            if (ternary) zero_run = 0;
            if (sorted[0] + sorted[1] + sorted[2] > (zero_run ? 4096u : 128u))
                for (int j = 0; j < 3; j++) freq[j] >>= 1;
            freq[ternary] += 2;
            if (ternary < 2) block[i] = (uint8_t)ternary;
            else {
                int index = next_symbol(&coder, high.frequency, high.count);
                if (index < 0) return -1;
                unsigned highbit = high.mapping[index];
                bump(&high, bump(&high, (unsigned)index, 256), 65536);
                if (!highbit) block[i] = 2;
                else {
                    Model *model = &low[highbit - 1];
                    index = next_symbol(&coder, model->frequency, model->count);
                    if (index < 0) return -1;
                    unsigned value = (1u << highbit) + model->mapping[index] + 1;
                    if (value > 255) return -1;
                    unsigned limit = model->count * 128;
                    bump(model, (unsigned)index, limit < 16384 ? limit : 16384);
                    block[i] = (uint8_t)value;
                }
            }
        }
        prev3 = prev2;
        prev2 = prev;
        prev = ternary;
    }
    return in->error ? -1 : 0;
}

static void m1ffn(uint8_t *block, uint32_t size)
{
    uint8_t table[256];
    for (unsigned i = 0; i < 256; i++) table[i] = (uint8_t)i;
    unsigned lasthead = 1;
    for (uint32_t i = 0; i < size; i++) {
        unsigned symbol = block[i];
        uint8_t value = table[symbol];
        block[i] = value;
        if (!symbol) lasthead = 0;
        else if (symbol == 1) {
            if (lasthead >= 2) { table[1] = table[0]; table[0] = value; }
        } else {
            memmove(table + 2, table + 1, symbol - 1);
            table[1] = value;
        }
        if (lasthead < 2) lasthead++;
    }
}

ptrdiff_t sitx_cyanide_decompress(const uint8_t *src, size_t src_size,
                                uint8_t *dest, size_t capacity)
{
    Input in = {src, src_size, 0, 0};
    size_t written = 0;
    read_byte(&in);
    while (!in.error) {
        unsigned marker = read_byte(&in);
        if (marker == 255)
            return in.pos == in.size && written <= PTRDIFF_MAX ? (ptrdiff_t)written : -1;
        if (marker != 0x77) return -1;
        uint32_t size = read_u32(&in), first = read_u32(&in);
        unsigned symbols = read_byte(&in);
        if (in.error || !size || first >= size || size > capacity - written ||
                (uint64_t)size * sizeof(uint32_t) > SIZE_MAX) return -1;
        uint8_t *block = malloc(size);
        uint32_t *transform = malloc((size_t)size * sizeof(uint32_t));
        if (!block || !transform || decode_block(&in, block, size, symbols) < 0) {
            free(block);
            free(transform);
            return -1;
        }
        m1ffn(block, size);
        uint32_t counts[256] = {0}, total = 0;
        for (uint32_t i = 0; i < size; i++) counts[block[i]]++;
        for (unsigned i = 0; i < 256; i++) {
            uint32_t count = counts[i];
            counts[i] = total;
            total += count;
        }
        for (uint32_t i = 0; i < size; i++) transform[counts[block[i]]++] = i;
        uint32_t index = first;
        for (uint32_t i = 0; i < size; i++) {
            index = transform[index];
            dest[written++] = block[index];
        }
        free(block);
        free(transform);
    }
    return -1;
}
