# Expert lab recipe (seed 1, level 1)

By-product of the reference run: what the scripted expert did, in order, with lab time.

- OPA wavelength 1300 nm. Parts bought: DL-C25 motorised delay stage, 4 x MIR-1 mirror, 1 x PER-1 periscope, CAM-VSWIR, GAP-TPA (EUR 10350; C_min = EUR 7450)
- Lab time: 113.2 min of 240 (47.2%), 110 tool calls
- Result: eta = 0.9965, R = 0.8694, O = 0.9966, |dt| = 0.5 fs

| # | t (min) | tool | args |
|---|---|---|---|
| 0 | 0.0 | read_manual | `{"device": "table"}` |
| 1 | 0.0 | read_manual | `{"device": "opa"}` |
| 2 | 0.0 | read_manual | `{"device": "delay_stage"}` |
| 3 | 0.0 | read_manual | `{"device": "sample_mount"}` |
| 4 | 15.0 | buy | `{"items": {"DL-C25": 1, "MIR-1": 4, "PER-1": 1, "GAP-TPA": 1, "CAM-VSWIR": 1}}` |
| 5 | 20.1 | place | `{"part": "sample", "x": 1300.0, "z": 600.0, "height": 120.0, "yaw_deg": 180.0}` |
| 6 | 20.2 | unblock | `{"arm": "opa"}` |
| 7 | 25.4 | place | `{"part": "periscope-1", "x": 2050.0, "z": 935.0, "height": 120.0, "yaw_deg": 180.0, "height_in": 158.0}` |
| 8 | 25.9 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 9 | 26.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 10 | 26.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": 8.5714}` |
| 11 | 27.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 12 | 27.9 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": 8.5714}` |
| 13 | 28.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 14 | 28.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -10.6547}` |
| 15 | 29.4 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -8.9081}` |
| 16 | 29.9 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 17 | 30.5 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -1.2906}` |
| 18 | 31.0 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -1.0311}` |
| 19 | 31.5 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 20 | 36.5 | place | `{"part": "mirror-1", "x": 1700.0, "z": 935.0, "height": 120.0, "yaw_deg": -45.0}` |
| 21 | 37.1 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 22 | 37.6 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 23 | 38.2 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 8.7464}` |
| 24 | 38.8 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 25 | 39.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 8.7464}` |
| 26 | 40.1 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 27 | 40.7 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 6.382}` |
| 28 | 41.2 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -10.1343}` |
| 29 | 41.9 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 30 | 42.5 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 0.6498}` |
| 31 | 43.0 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 0.8471}` |
| 32 | 43.6 | ir_card | `{"x": 1700.0, "z": 592.0, "height": 120.0}` |
| 33 | 48.6 | place | `{"part": "mirror-2", "x": 1700.0, "z": 592.0, "height": 120.0, "yaw_deg": 135.0}` |
| 34 | 49.1 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 35 | 49.6 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 36 | 50.1 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 7.5}` |
| 37 | 50.6 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 38 | 51.2 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 7.5}` |
| 39 | 51.7 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 40 | 52.2 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 5.5781}` |
| 41 | 52.7 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -8.4833}` |
| 42 | 53.2 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 43 | 53.7 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.4708}` |
| 44 | 54.2 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -1.0548}` |
| 45 | 54.7 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 46 | 55.2 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.0536}` |
| 47 | 55.7 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 1.0191}` |
| 48 | 56.3 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 49 | 56.8 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 0.3069}` |
| 50 | 57.3 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -0.8313}` |
| 51 | 57.8 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 52 | 57.9 | unblock | `{"arm": "800nm"}` |
| 53 | 63.0 | place | `{"part": "stage", "x": 781.5, "z": 309.0, "height": 120.0, "yaw_deg": 180.0}` |
| 54 | 63.5 | ir_card | `{"x": 1500.0, "z": 324.0, "height": 120.0}` |
| 55 | 68.5 | place | `{"part": "mirror-3", "x": 1500.0, "z": 325.9, "height": 119.1, "yaw_deg": 135.0}` |
| 56 | 69.2 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 57 | 69.7 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 58 | 70.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 10.6345}` |
| 59 | 71.0 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 60 | 71.6 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": 10.6345}` |
| 61 | 72.2 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 62 | 72.9 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -12.5365}` |
| 63 | 73.4 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -10.3206}` |
| 64 | 74.0 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 65 | 74.7 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -0.7922}` |
| 66 | 75.2 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -1.3527}` |
| 67 | 75.8 | ir_card | `{"x": 1500.0, "z": 608.0, "height": 120.0}` |
| 68 | 80.8 | place | `{"part": "mirror-4", "x": 1500.0, "z": 608.0, "height": 120.0, "yaw_deg": 225.0}` |
| 69 | 81.3 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 70 | 81.8 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 71 | 82.3 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 15.0}` |
| 72 | 82.8 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 73 | 83.3 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 15.0}` |
| 74 | 83.8 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 75 | 84.3 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -8.4178}` |
| 76 | 84.8 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -15.183}` |
| 77 | 85.3 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 78 | 85.5 | block | `{"arm": "800nm"}` |
| 79 | 85.7 | view_camera | `{"plane": "sample"}` |
| 80 | 85.8 | unblock | `{"arm": "800nm"}` |
| 81 | 85.9 | view_camera | `{"plane": "sample"}` |
| 82 | 86.1 | view_camera | `{"plane": "sample"}` |
| 83 | 86.7 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.3}` |
| 84 | 86.9 | view_camera | `{"plane": "sample"}` |
| 85 | 87.1 | view_camera | `{"plane": "sample"}` |
| 86 | 87.7 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.3}` |
| 87 | 88.0 | view_camera | `{"plane": "sample"}` |
| 88 | 88.1 | view_camera | `{"plane": "sample"}` |
| 89 | 88.7 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 4.2769}` |
| 90 | 89.2 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.6341}` |
| 91 | 89.5 | view_camera | `{"plane": "sample"}` |
| 92 | 89.6 | view_camera | `{"plane": "sample"}` |
| 93 | 90.2 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.1744}` |
| 94 | 90.7 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.288}` |
| 95 | 91.0 | view_camera | `{"plane": "sample"}` |
| 96 | 91.1 | view_camera | `{"plane": "sample"}` |
| 97 | 91.7 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.0107}` |
| 98 | 92.2 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.0161}` |
| 99 | 92.5 | view_camera | `{"plane": "sample"}` |
| 100 | 92.7 | view_camera | `{"plane": "sample"}` |
| 101 | 99.8 | scan | `{"start_mm": 11.0, "end_mm": 14.0, "step_mm": 0.005, "t_int": 0.4}` |
| 102 | 104.6 | scan | `{"start_mm": 9.0, "end_mm": 11.0, "step_mm": 0.005, "t_int": 0.4}` |
| 103 | 109.3 | scan | `{"start_mm": 14.0, "end_mm": 16.0, "step_mm": 0.005, "t_int": 0.4}` |
| 104 | 112.7 | scan | `{"start_mm": 14.053, "end_mm": 14.137, "step_mm": 0.001, "t_int": 2.0}` |
| 105 | 112.7 | move_stage | `{"position_mm": 14.04478}` |
| 106 | 112.8 | move_stage | `{"position_mm": 14.09478}` |
| 107 | 113.0 | view_camera | `{"plane": "sample"}` |
| 108 | 113.2 | view_camera | `{"plane": "sample"}` |
| 109 | 113.2 | submit | `{}` |
