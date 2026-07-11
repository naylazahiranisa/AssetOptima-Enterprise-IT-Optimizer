import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/theme_provider.dart';
import 'features/auth/models/auth_state.dart';
import 'features/auth/providers/auth_provider.dart';

class AssetOptimaField extends ConsumerWidget {
  const AssetOptimaField({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeProvider);

    ref.listen(authProvider, (prev, next) {
      next.whenData((state) {
        if (state is Unauthenticated) {
          router.go('/login');
        } else if (state is Authenticated) {
          router.go('/dashboard');
        }
      });
    });

    return MaterialApp.router(
      title: 'AssetOptima Field',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
