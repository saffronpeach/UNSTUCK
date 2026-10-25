import test from 'node:test';
import assert from 'node:assert/strict';
import { FocusTimer } from '../static/timer.js';
const setup = () => {
  let time = 1000;
  return { timer: new FocusTimer(() => time), advance: (ms) => { time += ms; } };
};
test('defaults and duration bounds', () => {
  const { timer } = setup();
  assert.equal(timer.display, '07:00');
  for (const invalid of [4, 11, 5.5, NaN]) { timer.setMinutes(invalid); assert.equal(timer.minutes, 7); }
  timer.setMinutes(5); assert.equal(timer.display, '05:00');
});
test('start and pause preserve elapsed time; resume ignores paused time', () => {
  const { timer, advance } = setup();
  timer.start(); advance(30000); timer.pause();
  assert.equal(timer.display, '06:30');
  advance(90000); assert.equal(timer.display, '06:30');
  timer.start(); advance(30000); assert.equal(timer.display, '06:00');
});
test('reset stops time and preserves selected duration', () => {
  const { timer, advance } = setup();
  timer.setMinutes(10); timer.start(); advance(12345); timer.reset();
  advance(90000); assert.equal(timer.display, '10:00'); assert.equal(timer.phase, 'ready');
});
test('background delay crosses expiry without going negative', () => {
  const { timer, advance } = setup();
  timer.start(); advance(999999); assert.equal(timer.display, '00:00'); assert.equal(timer.phase, 'expired');
  timer.pause(); timer.start(); assert.equal(timer.phase, 'expired'); assert.equal(timer.deadline, null);
});
test('completion early stops countdown and cannot resume', () => {
  const { timer, advance } = setup();
  timer.start(); advance(5000); timer.complete(); advance(700000); timer.start();
  assert.equal(timer.display, '06:55'); assert.equal(timer.phase, 'complete');
});
test('duration cannot change while running or paused', () => {
  const { timer } = setup();
  timer.start(); timer.setMinutes(5); assert.equal(timer.minutes, 7);
  timer.pause(); timer.setMinutes(10); assert.equal(timer.minutes, 7);
});
test('last partial second stays visible and full seven-minute session expires', () => {
  const { timer, advance } = setup();
  timer.start();
  for (let minute = 0; minute < 6; minute++) { advance(60000); timer.tick(); assert.equal(timer.phase, 'running'); }
  advance(59999); assert.equal(timer.display, '00:01');
  advance(1); assert.equal(timer.display, '00:00'); assert.equal(timer.phase, 'expired');
  timer.complete(); assert.equal(timer.phase, 'complete');
});
