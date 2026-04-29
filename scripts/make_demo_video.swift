import AppKit
import AVFoundation
import CoreVideo
import Foundation

struct Scene {
    let title: String
    let caption: String
    let prompt: String
    let tool: String
    let output: [String]
    let metrics: [(String, String, String)]
    let seconds: Double
}

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let assets = root.appendingPathComponent("assets")
let outDir = assets.appendingPathComponent("demo")
try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

let audioURL = outDir.appendingPathComponent("autoresearch-voiceover.aiff")
let silentVideoURL = outDir.appendingPathComponent("autoresearch-demo-silent.mp4")
let outputURL = assets.appendingPathComponent("autoresearch-demo.mp4")
try? FileManager.default.removeItem(at: silentVideoURL)
try? FileManager.default.removeItem(at: outputURL)

let scenes = [
    Scene(
        title: "Use case: improve trial-to-paid conversion",
        caption: "A SaaS team asks Codex to run a measured improvement loop.",
        prompt: "@autoresearch improve trial-to-paid conversion",
        tool: "autoresearch_start + kpi_interview_questions",
        output: [
            "Need north-star, KPIs, guardrails, browser access, iteration count",
            "Suggested KPIs: conversion_rate, retention_d7, p95_latency_ms",
            "Guardrail: error_rate below 2%"
        ],
        metrics: [("conversion", "3.1%", "baseline"), ("retention D7", "22%", "baseline"), ("p95 latency", "712 ms", "baseline")],
        seconds: 11
    ),
    Scene(
        title: "Fast forward: profile confirmed",
        caption: "The user answers once; Autoresearch saves the KPI operating model.",
        prompt: "Use conversion_rate + retention_d7; guard error_rate; run 3 iterations",
        tool: "save_kpi_profile",
        output: [
            "North star: increase qualified trial-to-paid conversion",
            "Iterations: 3 daily cycles",
            "Targets: conversion 5.5%, retention 30%, p95 450 ms"
        ],
        metrics: [("conversion", "3.1% -> 5.5%", "target"), ("retention D7", "22% -> 30%", "target"), ("p95 latency", "712 -> 450 ms", "target")],
        seconds: 11
    ),
    Scene(
        title: "Fast forward: Codex plans the work",
        caption: "The MCP server converts the profile into subagent briefs.",
        prompt: "@autoresearch generate the 3-iteration plan",
        tool: "generate_subagent_plan",
        output: [
            "Instrumentation auditor: validate KPI pipeline",
            "Product experimenter: reversible funnel experiments",
            "Performance optimizer: remove critical-path latency blockers"
        ],
        metrics: [("focus KPI", "p95 latency", "ranked"), ("plan", "3 agents", "ready"), ("risk", "attribution gap", "tracked")],
        seconds: 12
    ),
    Scene(
        title: "Fast forward: experiments learn",
        caption: "Results, feedback, and shortcomings are remembered for the next cycle.",
        prompt: "@autoresearch record iteration 2 outcome and next bet",
        tool: "record_experiment_result + update_kpi_snapshot",
        output: [
            "Latency improved while conversion moved up",
            "Shortcoming: aggregate-only snapshots hide attribution",
            "Next bet: add segment-level KPI decomposition"
        ],
        metrics: [("conversion", "3.4% -> 3.6%", "+0.2 pts"), ("retention D7", "23.5% -> 24.1%", "+0.6 pts"), ("p95 latency", "680 -> 650 ms", "-30 ms")],
        seconds: 12
    ),
    Scene(
        title: "Result: dashboard plus memory",
        caption: "The next @autoresearch run starts with evidence, not a blank prompt.",
        prompt: "@autoresearch render dashboard and continue from memory",
        tool: "render_dashboard",
        output: [
            "Latest smoke test completed end to end",
            "Known gap: plugin/browser enablement needs clear user prompt",
            "Next bet: final submission assets and marketplace metadata"
        ],
        metrics: [("conversion", "3.8%", "+0.7 pts"), ("retention D7", "24.7%", "+2.7 pts"), ("p95 latency", "620 ms", "-92 ms")],
        seconds: 14
    )
]

let width = 1280
let height = 720
let fps: Int32 = 30
let totalSeconds = scenes.reduce(0) { $0 + $1.seconds }

func attrs(_ size: CGFloat, _ weight: NSFont.Weight, _ color: NSColor, _ align: NSTextAlignment = .left) -> [NSAttributedString.Key: Any] {
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = align
    paragraph.lineSpacing = 3
    return [.font: NSFont.systemFont(ofSize: size, weight: weight), .foregroundColor: color, .paragraphStyle: paragraph]
}

func drawText(_ text: String, _ rect: CGRect, _ attributes: [NSAttributedString.Key: Any]) {
    NSString(string: text).draw(in: rect, withAttributes: attributes)
}

func round(_ rect: CGRect, _ radius: CGFloat, _ fill: NSColor, stroke: NSColor? = nil) {
    let path = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius)
    fill.setFill()
    path.fill()
    if let stroke {
        stroke.setStroke()
        path.lineWidth = 1
        path.stroke()
    }
}

func drawBrowserChrome(_ rect: CGRect) {
    round(rect, 18, NSColor(calibratedRed: 0.94, green: 0.96, blue: 0.98, alpha: 1))
    round(CGRect(x: rect.minX, y: rect.maxY - 46, width: rect.width, height: 46), 18, NSColor(calibratedRed: 0.88, green: 0.91, blue: 0.94, alpha: 1))
    for i in 0..<3 {
        round(CGRect(x: rect.minX + 22 + CGFloat(i) * 20, y: rect.maxY - 29, width: 10, height: 10), 5, [NSColor.systemRed, NSColor.systemYellow, NSColor.systemGreen][i])
    }
    round(CGRect(x: rect.minX + 110, y: rect.maxY - 34, width: rect.width - 150, height: 22), 11, .white)
    drawText("chatgpt.com  /  @autoresearch", CGRect(x: rect.minX + 130, y: rect.maxY - 29, width: rect.width - 190, height: 18), attrs(12, .medium, .darkGray))
}

func render(scene: Scene, index: Int, progress: Double, globalProgress: Double, context: CGContext) {
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)

    let bg = NSColor(calibratedRed: 0.035, green: 0.045, blue: 0.055, alpha: 1)
    bg.setFill()
    CGRect(x: 0, y: 0, width: width, height: height).fill()

    let teal = NSColor(calibratedRed: 0.15, green: 0.75, blue: 0.64, alpha: 1)
    let blue = NSColor(calibratedRed: 0.28, green: 0.55, blue: 0.92, alpha: 1)
    NSGradient(colors: [teal.withAlphaComponent(0.24), blue.withAlphaComponent(0.18), .clear])!.draw(in: CGRect(x: -120 + 180 * CGFloat(globalProgress), y: 0, width: 1500, height: 720), angle: 22)

    drawText("Autoresearch", CGRect(x: 56, y: 660, width: 240, height: 32), attrs(25, .bold, .white))
    drawText("working demo, fast-forwarded", CGRect(x: 940, y: 663, width: 280, height: 24), attrs(16, .medium, .white.withAlphaComponent(0.68), .right))

    let left = CGRect(x: 56, y: 88, width: 390, height: 540)
    round(left, 18, NSColor(calibratedRed: 0.10, green: 0.12, blue: 0.15, alpha: 0.94), stroke: .white.withAlphaComponent(0.10))
    drawText(scene.title, CGRect(x: 86, y: 548, width: 330, height: 64), attrs(30, .bold, .white))
    drawText(scene.caption, CGRect(x: 86, y: 485, width: 330, height: 54), attrs(18, .medium, .white.withAlphaComponent(0.76)))
    round(CGRect(x: 86, y: 418, width: 330, height: 42), 12, teal.withAlphaComponent(0.16), stroke: teal.withAlphaComponent(0.4))
    drawText("Loop \(index + 1) / \(scenes.count)", CGRect(x: 104, y: 431, width: 140, height: 20), attrs(15, .bold, teal))
    let barWidth = 330 * CGFloat((Double(index) + progress) / Double(scenes.count))
    round(CGRect(x: 86, y: 392, width: 330, height: 8), 4, .white.withAlphaComponent(0.10))
    round(CGRect(x: 86, y: 392, width: barWidth, height: 8), 4, teal)

    var metricY: CGFloat = 318
    for metric in scene.metrics {
        round(CGRect(x: 86, y: metricY, width: 330, height: 58), 12, .black.withAlphaComponent(0.24), stroke: .white.withAlphaComponent(0.08))
        drawText(metric.0, CGRect(x: 106, y: metricY + 32, width: 140, height: 18), attrs(14, .medium, .white.withAlphaComponent(0.62)))
        drawText(metric.1, CGRect(x: 106, y: metricY + 10, width: 160, height: 24), attrs(20, .bold, .white))
        drawText(metric.2, CGRect(x: 272, y: metricY + 16, width: 120, height: 22), attrs(14, .semibold, teal, .right))
        metricY -= 70
    }

    let browser = CGRect(x: 486, y: 88, width: 738, height: 540)
    drawBrowserChrome(browser)
    let body = CGRect(x: browser.minX + 24, y: browser.minY + 24, width: browser.width - 48, height: browser.height - 84)
    round(body, 16, .white)

    let chatX = body.minX + 28
    let userWidth: CGFloat = min(540, 250 + 310 * CGFloat(progress))
    round(CGRect(x: chatX + 92, y: body.maxY - 94, width: userWidth, height: 50), 16, blue.withAlphaComponent(0.22))
    drawText(scene.prompt, CGRect(x: chatX + 112, y: body.maxY - 75, width: userWidth - 34, height: 22), attrs(17, .medium, NSColor(calibratedRed: 0.06, green: 0.10, blue: 0.16, alpha: 1)))

    round(CGRect(x: chatX, y: body.maxY - 174, width: 420, height: 52), 14, NSColor(calibratedRed: 0.08, green: 0.11, blue: 0.16, alpha: 1))
    drawText("Tool call: \(scene.tool)", CGRect(x: chatX + 20, y: body.maxY - 154, width: 370, height: 20), attrs(16, .semibold, .white))

    var y = body.maxY - 246
    let visibleRows = min(scene.output.count, max(1, Int(progress * 5.0)))
    for i in 0..<visibleRows {
        round(CGRect(x: chatX, y: y, width: 620, height: 42), 10, NSColor(calibratedRed: 0.93, green: 0.96, blue: 0.98, alpha: 1))
        drawText(scene.output[i], CGRect(x: chatX + 18, y: y + 13, width: 580, height: 18), attrs(15, .medium, NSColor(calibratedRed: 0.08, green: 0.12, blue: 0.18, alpha: 1)))
        y -= 54
    }

    let cursorX = body.minX + 56 + CGFloat(progress) * 560
    let cursorY = body.minY + 54 + sin(CGFloat(progress) * .pi * 2) * 16
    let cursor = NSBezierPath()
    cursor.move(to: CGPoint(x: cursorX, y: cursorY + 32))
    cursor.line(to: CGPoint(x: cursorX + 20, y: cursorY - 16))
    cursor.line(to: CGPoint(x: cursorX + 28, y: cursorY + 2))
    cursor.line(to: CGPoint(x: cursorX + 46, y: cursorY - 4))
    cursor.close()
    NSColor.black.withAlphaComponent(0.52).setFill()
    cursor.fill()

    if index == scenes.count - 1 {
        let dashURL = assets.appendingPathComponent("autoresearch-dashboard.png")
        if let image = NSImage(contentsOf: dashURL) {
            image.draw(in: CGRect(x: body.minX + 60, y: body.minY + 54, width: 560, height: 354), from: .zero, operation: .sourceOver, fraction: 0.95)
        }
    }

    NSGraphicsContext.restoreGraphicsState()
}

let writer = try AVAssetWriter(outputURL: silentVideoURL, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 4_500_000]
])
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height
])
writer.add(input)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

var frame: Int64 = 0
var elapsed = 0.0
for (index, scene) in scenes.enumerated() {
    let frameCount = Int(scene.seconds * Double(fps))
    for i in 0..<frameCount {
        while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.002) }
        var buffer: CVPixelBuffer?
        CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32ARGB, nil, &buffer)
        guard let pixel = buffer else { fatalError("pixel buffer failed") }
        CVPixelBufferLockBaseAddress(pixel, [])
        let ctx = CGContext(data: CVPixelBufferGetBaseAddress(pixel), width: width, height: height, bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(pixel), space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
        let local = Double(i) / max(1, Double(frameCount - 1))
        render(scene: scene, index: index, progress: local, globalProgress: (elapsed + local * scene.seconds) / totalSeconds, context: ctx)
        adaptor.append(pixel, withPresentationTime: CMTime(value: frame, timescale: fps))
        CVPixelBufferUnlockBaseAddress(pixel, [])
        frame += 1
    }
    elapsed += scene.seconds
}
input.markAsFinished()
let writeGroup = DispatchGroup()
writeGroup.enter()
writer.finishWriting { writeGroup.leave() }
writeGroup.wait()

let composition = AVMutableComposition()
let videoAsset = AVURLAsset(url: silentVideoURL)
let audioAsset = AVURLAsset(url: audioURL)
let videoTrack = videoAsset.tracks(withMediaType: .video).first!
let compVideo = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)!
try compVideo.insertTimeRange(CMTimeRange(start: .zero, duration: videoAsset.duration), of: videoTrack, at: .zero)
if let audioTrack = audioAsset.tracks(withMediaType: .audio).first {
    let compAudio = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)!
    try compAudio.insertTimeRange(CMTimeRange(start: .zero, duration: min(audioAsset.duration, videoAsset.duration)), of: audioTrack, at: .zero)
}

let export = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality)!
export.outputURL = outputURL
export.outputFileType = .mp4
export.shouldOptimizeForNetworkUse = true
let exportGroup = DispatchGroup()
exportGroup.enter()
export.exportAsynchronously { exportGroup.leave() }
exportGroup.wait()
if export.status != .completed {
    fatalError(export.error?.localizedDescription ?? "export failed")
}
print(outputURL.path)
