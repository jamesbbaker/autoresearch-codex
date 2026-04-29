import AppKit
import AVFoundation
import CoreVideo
import Foundation

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let assets = root.appendingPathComponent("assets")
let transcriptURL = assets.appendingPathComponent("demo/real_demo_transcript.txt")
let outputURL = assets.appendingPathComponent("autoresearch-demo.mp4")
let silentURL = assets.appendingPathComponent("demo/autoresearch-real-demo-silent.mp4")
try? FileManager.default.removeItem(at: outputURL)
try? FileManager.default.removeItem(at: silentURL)

let rawLines = try String(contentsOf: transcriptURL).split(separator: "\n", omittingEmptySubsequences: false).map(String.init)
let width = 1280
let height = 720
let fps: Int32 = 30
let seconds = 74
let totalFrames = seconds * Int(fps)
let visibleRows = 25

func attrs(size: CGFloat, weight: NSFont.Weight, color: NSColor) -> [NSAttributedString.Key: Any] {
    [.font: NSFont.monospacedSystemFont(ofSize: size, weight: weight), .foregroundColor: color]
}

func drawText(_ text: String, x: CGFloat, y: CGFloat, width: CGFloat, size: CGFloat = 20, color: NSColor = .white, weight: NSFont.Weight = .regular) {
    NSString(string: text).draw(in: CGRect(x: x, y: y, width: width, height: size + 8), withAttributes: attrs(size: size, weight: weight, color: color))
}

func rounded(_ rect: CGRect, radius: CGFloat, fill: NSColor, stroke: NSColor? = nil) {
    let path = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius)
    fill.setFill()
    path.fill()
    if let stroke {
        stroke.setStroke()
        path.lineWidth = 1
        path.stroke()
    }
}

func color(for line: String) -> NSColor {
    if line.hasPrefix("$") { return NSColor(calibratedRed: 0.27, green: 0.90, blue: 0.70, alpha: 1) }
    if line.hasPrefix("FAIL") || line.contains("0/3") || line.hasPrefix("-") { return NSColor(calibratedRed: 1.00, green: 0.42, blue: 0.42, alpha: 1) }
    if line.hasPrefix("PASS") || line.contains("3/3") || line.hasPrefix("+") { return NSColor(calibratedRed: 0.45, green: 0.95, blue: 0.55, alpha: 1) }
    if line.contains("MCP") || line.contains("Autoresearch") || line.contains("Codex") { return NSColor(calibratedRed: 0.56, green: 0.72, blue: 1.0, alpha: 1) }
    return NSColor(calibratedRed: 0.86, green: 0.89, blue: 0.92, alpha: 1)
}

func render(frameIndex: Int, context: CGContext) {
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)

    NSColor(calibratedRed: 0.035, green: 0.045, blue: 0.055, alpha: 1).setFill()
    CGRect(x: 0, y: 0, width: width, height: height).fill()

    NSGradient(colors: [
        NSColor(calibratedRed: 0.04, green: 0.28, blue: 0.22, alpha: 0.75),
        NSColor(calibratedRed: 0.06, green: 0.09, blue: 0.16, alpha: 0.15),
    ])!.draw(in: CGRect(x: 0, y: 0, width: width, height: height), angle: 18)

    drawText("Autoresearch MCP + Codex CLI", x: 56, y: 658, width: 620, size: 26, color: .white, weight: .bold)
    drawText("real fake-repo test: failing KPI code -> Codex patch -> passing tests", x: 56, y: 628, width: 780, size: 16, color: .white.withAlphaComponent(0.68))
    drawText("No voiceover. Actual commands and code diff.", x: 900, y: 642, width: 300, size: 15, color: .white.withAlphaComponent(0.65))

    let terminal = CGRect(x: 56, y: 54, width: 1168, height: 550)
    rounded(terminal, radius: 18, fill: NSColor(calibratedRed: 0.02, green: 0.025, blue: 0.032, alpha: 0.96), stroke: .white.withAlphaComponent(0.12))
    rounded(CGRect(x: terminal.minX, y: terminal.maxY - 42, width: terminal.width, height: 42), radius: 18, fill: NSColor(calibratedRed: 0.08, green: 0.09, blue: 0.11, alpha: 1))
    for i in 0..<3 {
        rounded(CGRect(x: terminal.minX + 22 + CGFloat(i) * 20, y: terminal.maxY - 26, width: 10, height: 10), radius: 5, fill: [NSColor.systemRed, NSColor.systemYellow, NSColor.systemGreen][i])
    }
    drawText("sample-saas - trial funnel KPI loop", x: terminal.minX + 96, y: terminal.maxY - 30, width: 600, size: 14, color: .white.withAlphaComponent(0.62))

    let progress = Double(frameIndex) / Double(totalFrames - 1)
    let reveal = min(rawLines.count, max(1, Int(progress * Double(rawLines.count + visibleRows))))
    let start = max(0, reveal - visibleRows)
    let end = min(rawLines.count, reveal)
    let shown = Array(rawLines[start..<end])

    var y = terminal.maxY - 78
    for line in shown {
        let clipped = line.count > 112 ? String(line.prefix(109)) + "..." : line
        drawText(clipped, x: terminal.minX + 28, y: y, width: terminal.width - 56, size: 17, color: color(for: clipped), weight: clipped.hasPrefix("$") ? .semibold : .regular)
        y -= 20
    }

    if frameIndex % 40 < 22 {
        rounded(CGRect(x: terminal.minX + 28 + CGFloat((shown.last ?? "").prefix(80).count) * 10.0, y: y + 20, width: 9, height: 18), radius: 2, fill: .white.withAlphaComponent(0.72))
    }

    let bar = CGRect(x: 56, y: 26, width: 1168, height: 8)
    rounded(bar, radius: 4, fill: .white.withAlphaComponent(0.10))
    rounded(CGRect(x: bar.minX, y: bar.minY, width: bar.width * CGFloat(progress), height: bar.height), radius: 4, fill: NSColor(calibratedRed: 0.27, green: 0.90, blue: 0.70, alpha: 1))

    NSGraphicsContext.restoreGraphicsState()
}

let writer = try AVAssetWriter(outputURL: silentURL, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 3_800_000],
])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height,
])
writer.add(input)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

for frame in 0..<totalFrames {
    while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.002) }
    var buffer: CVPixelBuffer?
    CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32ARGB, nil, &buffer)
    guard let pixel = buffer else { fatalError("pixel buffer failed") }
    CVPixelBufferLockBaseAddress(pixel, [])
    let context = CGContext(
        data: CVPixelBufferGetBaseAddress(pixel),
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(pixel),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
    )!
    render(frameIndex: frame, context: context)
    adaptor.append(pixel, withPresentationTime: CMTime(value: CMTimeValue(frame), timescale: fps))
    CVPixelBufferUnlockBaseAddress(pixel, [])
}

input.markAsFinished()
let group = DispatchGroup()
group.enter()
writer.finishWriting { group.leave() }
group.wait()
try FileManager.default.copyItem(at: silentURL, to: outputURL)
print(outputURL.path)
