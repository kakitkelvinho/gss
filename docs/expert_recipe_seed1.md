# Expert lab recipe (seed 1)

By-product of the reference run: what the scripted expert did, in order, with lab time.

- Parts bought: DL-C25 delay stage, BBO-T236 crystal, 4 x MIR-1 mirror, 1 x PER-1 periscope (EUR 4800; C_min = EUR 1900)
- Lab time: 148.2 min of 240 (61.8%), 110 tool calls
- Result: eta = 0.9948, R = 0.9129, O = 0.9964, |dt| = 2.8 fs

| # | t (min) | tool | args |
|---|---|---|---|
| 0 | 5.0 | read_manual | `{"device": "table"}` |
| 1 | 10.0 | read_manual | `{"device": "opa"}` |
| 2 | 15.0 | read_manual | `{"device": "delay_stage"}` |
| 3 | 20.0 | read_manual | `{"device": "sample_mount"}` |
| 4 | 35.0 | buy | `{"items": {"DL-C25": 1, "BBO-T236": 1, "MIR-1": 4, "PER-1": 1}}` |
| 5 | 40.1 | place | `{"part": "sample", "x": 1300.0, "z": 600.0, "height": 120.0, "yaw_deg": 180.0}` |
| 6 | 40.2 | unblock | `{"arm": "probe"}` |
| 7 | 45.4 | place | `{"part": "periscope-1", "x": 2050.0, "z": 935.0, "height": 120.0, "yaw_deg": 180.0, "height_in": 158.0}` |
| 8 | 45.9 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 9 | 46.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 10 | 46.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": 8.5714}` |
| 11 | 47.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 12 | 47.9 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": 8.5714}` |
| 13 | 48.4 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 14 | 48.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -10.6547}` |
| 15 | 49.4 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -8.9081}` |
| 16 | 49.9 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 17 | 50.5 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -1.2906}` |
| 18 | 51.0 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -1.0311}` |
| 19 | 51.5 | ir_card | `{"x": 1700.0, "z": 935.0, "height": 120.0}` |
| 20 | 56.5 | place | `{"part": "mirror-1", "x": 1700.0, "z": 935.0, "height": 120.0, "yaw_deg": -45.0}` |
| 21 | 57.0 | ir_card | `{"x": 1700.0, "z": 608.0, "height": 120.0}` |
| 22 | 57.5 | ir_card | `{"x": 1700.0, "z": 608.0, "height": 120.0}` |
| 23 | 58.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 9.1743}` |
| 24 | 58.5 | ir_card | `{"x": 1700.0, "z": 608.0, "height": 120.0}` |
| 25 | 59.0 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 9.1743}` |
| 26 | 59.5 | ir_card | `{"x": 1700.0, "z": 608.0, "height": 120.0}` |
| 27 | 60.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 5.9985}` |
| 28 | 60.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -10.5767}` |
| 29 | 61.0 | ir_card | `{"x": 1700.0, "z": 608.0, "height": 120.0}` |
| 30 | 61.5 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 0.8207}` |
| 31 | 62.0 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 0.8778}` |
| 32 | 62.5 | ir_card | `{"x": 1700.0, "z": 608.0, "height": 120.0}` |
| 33 | 67.5 | place | `{"part": "mirror-2", "x": 1700.0, "z": 608.0, "height": 120.0, "yaw_deg": 135.0}` |
| 34 | 68.0 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 35 | 68.5 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 36 | 69.0 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 7.5}` |
| 37 | 69.5 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 38 | 70.0 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 7.5}` |
| 39 | 70.5 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 40 | 71.0 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 6.0776}` |
| 41 | 71.5 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -8.4493}` |
| 42 | 72.1 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 43 | 72.6 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.737}` |
| 44 | 73.1 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -1.2434}` |
| 45 | 73.6 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 46 | 74.1 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 0.0698}` |
| 47 | 74.6 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 1.1979}` |
| 48 | 75.1 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 49 | 75.6 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 0.3215}` |
| 50 | 76.1 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -1.0008}` |
| 51 | 76.6 | ir_card | `{"x": 1300.0, "z": 608.0, "height": 120.0}` |
| 52 | 76.8 | unblock | `{"arm": "pump"}` |
| 53 | 81.9 | place | `{"part": "stage", "x": 784.5, "z": 306.0, "height": 120.0, "yaw_deg": 180.0}` |
| 54 | 82.4 | ir_card | `{"x": 1500.0, "z": 318.0, "height": 120.0}` |
| 55 | 87.4 | place | `{"part": "mirror-3", "x": 1500.0, "z": 319.9, "height": 119.1, "yaw_deg": 135.0}` |
| 56 | 87.9 | ir_card | `{"x": 1500.0, "z": 592.0, "height": 120.0}` |
| 57 | 88.4 | ir_card | `{"x": 1500.0, "z": 592.0, "height": 120.0}` |
| 58 | 88.9 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 11.0254}` |
| 59 | 89.4 | ir_card | `{"x": 1500.0, "z": 592.0, "height": 120.0}` |
| 60 | 89.9 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": 11.0254}` |
| 61 | 90.4 | ir_card | `{"x": 1500.0, "z": 592.0, "height": 120.0}` |
| 62 | 90.9 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -12.9972}` |
| 63 | 91.4 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -10.6999}` |
| 64 | 91.9 | ir_card | `{"x": 1500.0, "z": 592.0, "height": 120.0}` |
| 65 | 92.4 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -0.6431}` |
| 66 | 92.9 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -1.4101}` |
| 67 | 93.4 | ir_card | `{"x": 1500.0, "z": 592.0, "height": 120.0}` |
| 68 | 98.4 | place | `{"part": "mirror-4", "x": 1500.0, "z": 592.0, "height": 120.0, "yaw_deg": 225.0}` |
| 69 | 98.9 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 70 | 99.4 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 71 | 99.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 15.0}` |
| 72 | 100.4 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 73 | 100.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 15.0}` |
| 74 | 101.4 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 75 | 101.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -8.1547}` |
| 76 | 102.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -15.1812}` |
| 77 | 102.9 | ir_card | `{"x": 1300.0, "z": 592.0, "height": 120.0}` |
| 78 | 103.1 | block | `{"arm": "pump"}` |
| 79 | 103.3 | view_camera | `{"plane": "sample"}` |
| 80 | 103.4 | unblock | `{"arm": "pump"}` |
| 81 | 103.5 | view_camera | `{"plane": "sample"}` |
| 82 | 103.7 | view_camera | `{"plane": "sample"}` |
| 83 | 104.3 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.3}` |
| 84 | 104.5 | view_camera | `{"plane": "sample"}` |
| 85 | 104.7 | view_camera | `{"plane": "sample"}` |
| 86 | 105.3 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.3}` |
| 87 | 105.6 | view_camera | `{"plane": "sample"}` |
| 88 | 105.7 | view_camera | `{"plane": "sample"}` |
| 89 | 106.3 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 3.6142}` |
| 90 | 106.8 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.8213}` |
| 91 | 107.1 | view_camera | `{"plane": "sample"}` |
| 92 | 107.2 | view_camera | `{"plane": "sample"}` |
| 93 | 107.8 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.1521}` |
| 94 | 108.3 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.222}` |
| 95 | 108.6 | view_camera | `{"plane": "sample"}` |
| 96 | 108.7 | view_camera | `{"plane": "sample"}` |
| 97 | 109.3 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.0107}` |
| 98 | 109.8 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.0145}` |
| 99 | 110.1 | view_camera | `{"plane": "sample"}` |
| 100 | 110.3 | view_camera | `{"plane": "sample"}` |
| 101 | 113.3 | measure_path | `{"arm": "pump"}` |
| 102 | 116.3 | measure_path | `{"arm": "probe"}` |
| 103 | 116.3 | status | `{}` |
| 104 | 144.5 | scan | `{"start_mm": 7.1, "end_mm": 19.1, "step_mm": 0.005, "t_int": 0.4}` |
| 105 | 147.7 | scan | `{"start_mm": 14.105, "end_mm": 14.185, "step_mm": 0.001, "t_int": 2.0}` |
| 106 | 147.8 | move_stage | `{"position_mm": 14.14552}` |
| 107 | 148.0 | view_camera | `{"plane": "sample"}` |
| 108 | 148.1 | view_camera | `{"plane": "sample"}` |
| 109 | 148.2 | submit | `{}` |
